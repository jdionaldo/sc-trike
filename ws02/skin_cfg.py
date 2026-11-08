"""Skin selector: WS03_SKIN=concept builds/uses the reference-concept shell in out/mono3_concept; anything else is the current skin in out/mono3."""
import os
CONCEPT = os.environ.get("WS03_SKIN", "current") == "concept"
MONO = "out/mono3_concept" if CONCEPT else "out/mono3"
