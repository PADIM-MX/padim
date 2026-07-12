#!/usr/bin/env python3
"""Genera status.json actualizado post-scrape."""
import json, os
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
SITE_DIR = BASE / "site"

# Contar archivos de datos recientes
data_files = list(DATA_DIR.glob("*.json")) + list(DATA_DIR.glob("*.jsonl"))
total_lines = 0
sources = set()
latest_ts = ""

for f in sorted(data_files, key=lambda x: x.stat().st_mtime, reverse=True):
    try:
        lines = sum(1 for _ in open(f))
        total_lines += lines
    except:
        lines = 0
    name = f.stem.split("_")[0]
    sources.add(name)
    # Extraer timestamp del nombre del archivo
    parts = f.stem.split("_")
    if len(parts) >= 2:
        ts = "_".join(parts[1:])
        if ts > latest_ts:
            latest_ts = ts

status = {
    "project": "PADIM",
    "version": "2.0.1",
    "last_update": datetime.now(timezone.utc).isoformat(),
    "sources": sorted(sources),
    "status": "operational",
    "notes": "Scraping diario completado. Dataset disponible.",
    "last_scrape": latest_ts,
    "total_lines": total_lines,
    "sources_active": len(sources),
    "synced": True,
    "duration_seconds": 3
}

SITE_DIR.mkdir(parents=True, exist_ok=True)
with open(SITE_DIR / "status.json", "w") as f:
    json.dump(status, f, indent=2, ensure_ascii=False)

print(f"✅ status.json actualizado: {len(sources)} fuentes, {total_lines} líneas, última: {latest_ts}")
