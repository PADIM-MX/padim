#!/usr/bin/env python3
"""PADIM Metrics Updater — actualiza métricas en todas las landings desde la API en vivo."""
import json, subprocess, sys
from pathlib import Path

API = "http://localhost:8005/v1/system/metrics"
LANDINGS = [
    "/home/polaris/workspace/projects/BACKBONE/frontend/index.html",
    "/home/polaris/workspace/projects/BACKBONE/padim/site/index.html",
    "/home/polaris/workspace/projects/PADIM-scraper/site/index.html",
    "/home/polaris/workspace/projects/BACKBONE/frontend/socios-v2-premium.html",
]

def fetch_metrics():
    r = subprocess.run(["curl", "-s", "--max-time", "5", API], capture_output=True, text=True, timeout=10)
    if r.returncode != 0:
        print("Error: API no responde")
        sys.exit(1)
    return json.loads(r.stdout)

def update_file(path, total, geo):
    fp = Path(path)
    if not fp.exists():
        print(f"  ✗ {path} — no existe")
        return
    content = fp.read_text()
    old = content
    # Replace static numbers
    content = content.replace("53,207", f"{total:,}")
    content = content.replace("51,721", f"{total:,}")
    content = content.replace("51,557", f"{geo:,}")
    content = content.replace("52K+", f"{round(geo/1000)}K+")
    content = content.replace("52,000+", f"{geo:,}+")
    content = content.replace("51K+", f"{round(total/1000)}K+")
    if content != old:
        fp.write_text(content)
        print(f"  ✅ {path} — actualizado")
    else:
        print(f"  — {path} — sin cambios")

def main():
    metrics = fetch_metrics()
    total = metrics["total_properties"]
    # Get geo count
    r = subprocess.run(["docker","exec","backbone-postgres","psql","-U","backbone","-d","backbone","-t","-A",
        "-c","SELECT COUNT(*) FROM properties WHERE lat IS NOT NULL AND lng IS NOT NULL;"],
        capture_output=True, text=True, timeout=10)
    geo = int(r.stdout.strip()) if r.returncode == 0 else total

    print(f"API: {total:,} total · {geo:,} geolocalizadas")
    for landing in LANDINGS:
        update_file(landing, total, geo)

if __name__ == "__main__":
    main()