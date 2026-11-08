"""Skin selector: WS03_SKIN=concept builds/uses the rev 3-6 concept shell in out/mono3_concept, WS03_SKIN=facet the rev 7 faceted shell in out/mono3_facet;
anything else is the current skin in out/mono3."""
import os
_S = os.environ.get("WS03_SKIN", "current")
FACET = _S == "facet"
CONCEPT = _S in ("concept", "facet")                  # the facet skin shares the concept's interface changes (taller deck, posts, dowel pads)
MONO = "out/mono3_facet" if FACET else ("out/mono3_concept" if CONCEPT else "out/mono3")
