import collections
def closure(pn, show=25):
    cnt=collections.Counter()
    for p in pn:
        ids=p['ids']
        for k in range(len(ids)):
            cnt[frozenset((ids[k],ids[(k+1)%len(ids)]))]+=1
    bad=[tuple(sorted(e)) for e,c in cnt.items() if c!=2]
    return bad
