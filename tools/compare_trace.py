"""Compare the current STEP projection against the same traced reference pixels."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from parts.reference_trace import SIDE, TAIL, QUARTER, ROOF, HOOD, MM_PER_PIXEL, PIXEL_ROCKER, PIXEL_FRONT

root=Path(__file__).resolve().parents[1]
reference=root/'inputs'/'Screenshot 2026-11-10 at 2.44.31\u202fPM.png'
img=plt.imread(reference)
shape=cq.importers.importStep(str(root/'output/model.step')).val()
fig,axes=plt.subplots(2,1,figsize=(16,12),layout='constrained')
axes[0].imshow(img)
axes[0].set_title('Reference with manually traced shell edges (cyan) — wheels and mechanics excluded')
axes[1].set_facecolor('#f4f5f6')
axes[1].set_title('Current CAD side projection with the same trace (cyan dashed)')
polys=[]; lines=[]
for solid in shape.Solids():
    for f in solid.Faces():
        vertices,triangles=f.tessellate(.1)
        for tri in triangles:
            p=[vertices[i] for i in tri]
            q=[((v.y+139)/MM_PER_PIXEL+PIXEL_FRONT,PIXEL_ROCKER-v.z/MM_PER_PIXEL) for v in p]
            polys.append(q)
    for e in solid.Edges():
        pts=[e.startPoint(),e.endPoint()]
        lines.append([((v.y+139)/MM_PER_PIXEL+PIXEL_FRONT,PIXEL_ROCKER-v.z/MM_PER_PIXEL) for v in pts])
axes[1].add_collection(PolyCollection(polys,facecolors='#7c8791',edgecolors='none'))
axes[1].add_collection(LineCollection(lines,colors='#29343e',linewidths=.45,alpha=.65))
for ax in axes:
    for poly,close in [(SIDE,True),(TAIL,True),(QUARTER,True),(ROOF,False),(HOOD,False)]:
        xy=[(p[0],p[1]) for p in poly]
        if close:xy.append(xy[0])
        ax.plot(*zip(*xy),color='#00c8da',lw=1.8,ls='-' if ax is axes[0] else '--')
    ax.set_xlim(250,1460);ax.set_ylim(485,-10);ax.set_aspect('equal');ax.axis('off')
fig.savefig(root/'renders/traced-comparison.png',dpi=140)
fig.savefig(root/'renders/traced-comparison.svg')
print('Saved renders/traced-comparison.png and .svg')
