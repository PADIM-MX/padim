#!/usr/bin/env python3
"""PADIM — Exporta propiedades desde BACKBONE DB a propiedades.jsonl (NDJSON).
Usa psycopg2 para conectar directo a PostgreSQL. Filtra quality_score >= 0.50."""
import json, subprocess, sys
from pathlib import Path

OUTPUT = Path("/home/polaris/workspace/projects/PADIM-scraper/data/propiedades.jsonl")

def pg(sql):
    cmd = ["docker", "exec", "backbone-postgres", "psql", "-U", "backbone",
           "-d", "backbone", "-t", "-A", "-c", sql]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.stdout.strip() if r.returncode == 0 else None

def main():
    print("Exportando propiedades desde DB...")
    sql = """
    SELECT json_agg(row_to_json(t)) FROM (
        SELECT source, source_id, source_url, title, description,
               property_type, business_type, price::numeric, currency,
               m2_constructed::numeric, m2_land::numeric,
               bedrooms, bathrooms, parking,
               address, colony, municipality, state,
               lat::numeric, lng::numeric,
               images, agent_name,
               scraped_at::text, quality_score::numeric
        FROM properties
        WHERE quality_score >= 0.50
          AND price::numeric > 10000
        ORDER BY quality_score DESC, price DESC
        LIMIT 50000
    ) t;
    """
    raw = pg(sql)
    if not raw:
        print("Error: no data from DB")
        sys.exit(1)
    try:
        props = json.loads(raw)
    except json.JSONDecodeError:
        print("Error: invalid JSON from DB")
        sys.exit(1)
    if not isinstance(props, list):
        props = [props]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(OUTPUT, "w") as f:
        for p in props:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
            count += 1

    print(f"✅ {count} propiedades exportadas a {OUTPUT}")
    print(f"   Rango: quality >= 0.50, price > 10,000")

if __name__ == "__main__":
    main()