#!/usr/bin/env python3
"""
PADIM — Consolidación de datos a propiedades.jsonl + DB v2.0

Toma todos los archivos JSON en data/ (de cualquier portal, schema legacy o RESO),
los normaliza a schema RESO unificado, ejecuta Trust Engine, 
deduplica y guarda como NDJSON + sincroniza a DB.

Uso:
    python3 scripts/consolidate_to_jsonl.py [--dry-run]
"""
import json, hashlib, re, os, sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "propiedades.jsonl"


def load_json_files() -> list:
    """Carga todos los archivos JSON en data/"""
    all_props = []
    for f in sorted(DATA_DIR.glob("*.json")):
        if f.name == "propiedades.jsonl":
            continue  # no auto-referenciar
        try:
            with open(f) as fh:
                data = json.load(fh)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("precio", item.get("price", 0)) > 0:
                        item["_source_file"] = f.name
                        all_props.append(item)
                print(f"  📄 {f.name}: {len(data)} props")
            elif isinstance(data, dict):
                # Single object
                all_props.append(data)
                print(f"  📄 {f.name}: 1 prop")
        except Exception as e:
            print(f"  ⚠️  {f.name}: {e}")
    return all_props


def normalize_to_reso(item: dict, source_name: str = "") -> dict:
    """Normaliza cualquier schema (legacy o RESO) a RESO unificado PADIM"""
    
    # Detectar schema legacy (campos en español)
    portal = item.get("portal") or item.get("source") or source_name or "unknown"
    
    price = item.get("price") or item.get("precio") or 0
    if isinstance(price, str):
        price = int(float(price.replace(",", "").replace("$", "")))
    
    return {
        "source": portal,
        "source_id": item.get("source_id") or item.get("fingerprint") or item.get("postingId", ""),
        "source_url": item.get("source_url") or item.get("url") or item.get("listingUrl", ""),
        "title": item.get("title") or item.get("titulo") or "",
        "description": item.get("description") or item.get("descripcion") or item.get("generatedTitle") or None,
        "property_type": item.get("property_type") or item.get("tipo_inmueble") or "otro",
        "business_type": item.get("business_type") or item.get("tipo_operacion") or "venta",
        "price": int(price) if price else 0,
        "currency": "MXN",
        "price_m2": None,
        "m2_constructed": item.get("m2_constructed") or item.get("metros_cuadrados") or None,
        "m2_land": item.get("m2_land") or item.get("metros_terreno") or None,
        "bedrooms": item.get("bedrooms") or item.get("recamaras") or None,
        "bathrooms": item.get("bathrooms") or item.get("banos") or None,
        "parking": item.get("parking") or None,
        "address": item.get("address") or item.get("direccion") or "",
        "colony": item.get("colony") or item.get("colonia") or "",
        "municipality": item.get("municipality") or item.get("delegacion") or item.get("municipio") or "",
        "state": item.get("state") or item.get("estado") or "",
        "lat": item.get("lat") or item.get("latitud") or None,
        "lng": item.get("lng") or item.get("longitud") or None,
        "images": item.get("images") or item.get("fotos") or [],
        "agent_name": item.get("agent_name") or item.get("publisher", {}).get("name") if isinstance(item.get("publisher"), dict) else None,
        "scraped_at": item.get("scraped_at") or datetime.now(timezone.utc).isoformat(),
    }


def fingerprint_reso(prop: dict) -> str:
    """SHA256 fingerprint sobre campos canónicos RESO"""
    raw = f"{prop['source']}:{prop.get('source_id','')}:{prop.get('title','')}:{prop.get('price',0)}:{prop.get('colony','')}"
    return hashlib.sha256(raw.lower().strip().encode()).hexdigest()


def run_trust_engine_on(props: list) -> list:
    """Aplica Trust Engine a lista de props RESO"""
    try:
        sys.path.insert(0, str(BASE_DIR))
        from padim.engine.trust_engine import TrustEngine
        engine = TrustEngine()
        for prop in props:
            try:
                result = engine.analyze(
                    property_id=prop.get("source_id", fingerprint_reso(prop)),
                    source=prop.get("source", "unknown"),
                    title=prop.get("title", ""),
                    description=prop.get("description", ""),
                    price=prop.get("price", 0),
                    price_m2=None,
                    property_type=prop.get("property_type", "otro"),
                    last_updated=None,
                    days_on_market=None,
                    price_changes=0,
                    source_count=1,
                    colony=prop.get("colony", ""),
                    municipality=prop.get("municipality", ""),
                    agent_name=prop.get("agent_name"),
                    agent_properties_count=0,
                )
                prop["trust_score"] = round(result.trust_score, 2)
                prop["is_relevant"] = result.is_relevant
                prop["is_suspicious"] = result.is_suspicious
                prop["signals"] = [s.type.value for s in result.signals]
            except Exception as e:
                prop["trust_score"] = 0.5
                prop["trust_error"] = str(e)
    except ImportError:
        print("  ⚠️  Trust Engine no disponible, asignando score 0.5")
        for prop in props:
            prop["trust_score"] = 0.5
            prop["is_relevant"] = True
            prop["is_suspicious"] = False
            prop["signals"] = []
    return props


def deduplicate(props: list) -> list:
    """Deduplica por fingerprint (último gana)"""
    seen = {}
    for prop in props:
        fp = fingerprint_reso(prop)
        seen[fp] = prop  # último gana (más reciente)
    deduped = list(seen.values())
    saved = len(props) - len(deduped)
    if saved:
        print(f"  🗑️  {saved} duplicados eliminados")
    return deduped


def save_to_padim_db(prop: dict) -> bool:
    """Guarda propiedad en PostgreSQL de PADIM"""
    conn = None
    try:
        import psycopg2
        from uuid import uuid4
        
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "padim"),
            password=os.getenv("DB_PASSWORD", ""),
            dbname=os.getenv("DB_NAME", "padim")
        )
        cur = conn.cursor()
        
        source_id = prop.get("source_id", str(uuid4()))
        price = float(prop.get("price", 0)) if prop.get("price") else 0
        m2 = float(prop["m2_constructed"]) if prop.get("m2_constructed") is not None else None
        beds = int(prop["bedrooms"]) if prop.get("bedrooms") is not None else None
        baths = float(prop["bathrooms"]) if prop.get("bathrooms") is not None else None

        cur.execute("""
            INSERT INTO properties 
                (id, source, source_id, source_url, title, description,
                 property_type, business_type, price, currency,
                 m2_constructed, bedrooms, bathrooms,
                 address, colony, state, images, scraped_at)
            VALUES 
                (%s, %s, %s, %s, %s, %s,
                 %s, %s, %s, %s,
                 %s, %s, %s,
                 %s, %s, %s, %s::json, NOW())
            ON CONFLICT (source, source_id) 
            DO UPDATE SET 
                price = EXCLUDED.price,
                last_updated = NOW(),
                title = EXCLUDED.title
        """, (
            str(uuid4()), prop.get("source", "padim"), source_id,
            prop.get("source_url", ""), prop.get("title", ""), prop.get("description", ""),
            prop.get("property_type", ""), prop.get("business_type", "venta"),
            price, prop.get("currency", "MXN"),
            m2, beds, baths,
            prop.get("address", ""), prop.get("colony", ""),
            prop.get("state", ""),
            json.dumps(prop.get("images", []))
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"    ⚠️  DB error: {e}")
        return False
    finally:
        try:
            if conn:
                conn.close()
        except:
            pass


def main():
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("🏃 Dry-run activado (solo muestra, no escribe)\n")
    
    print(f"🔍 PADIM Consolidator v2.0")
    print(f"   Input: {DATA_DIR}/*.json")
    print(f"   Output: {OUTPUT_FILE}\n")
    
    # 1. Cargar todos los archivos
    all_props = load_json_files()
    if not all_props:
        print("\n⚠️  No se encontraron propiedades para consolidar")
        return 1
    
    print(f"\n📥 Total crudo: {len(all_props)} propiedades")
    
    # 2. Normalizar a RESO
    reso_props = [normalize_to_reso(p) for p in all_props]
    print(f"🔄 Normalizadas a schema RESO: {len(reso_props)}")
    
    # 3. Trust Engine
    print("🧠 Aplicando Trust Engine...")
    reso_props = run_trust_engine_on(reso_props)
    avg_trust = sum(p.get("trust_score", 0.5) for p in reso_props) / len(reso_props)
    real = sum(1 for p in reso_props if p.get("is_relevant", True) and p.get("trust_score", 0.5) >= 0.3)
    ghosts = sum(1 for p in reso_props if not p.get("is_relevant", True))
    susp = sum(1 for p in reso_props if p.get("is_suspicious", False))
    print(f"   Trust promedio: {avg_trust:.2f}")
    print(f"   Reales: {real} | Fantasmas: {ghosts} | Sospechosas: {susp}")
    
    # 4. Deduplicar
    print("🔗 Deduplicando...")
    deduped = deduplicate(reso_props)
    print(f"   Únicas: {len(deduped)} ({len(reso_props) - len(deduped)} duplicados eliminados)")
    
    if dry_run:
        print(f"\n🏁 Dry-run — no se escribió nada")
        print(f"   Se habrían guardado {len(deduped)} props en {OUTPUT_FILE}")
        return 0
    
    # 5. Guardar como NDJSON
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        for prop in deduped:
            # Limpiar campo interno
            prop.pop("_source_file", None)
            f.write(json.dumps(prop, ensure_ascii=False) + "\n")
    print(f"\n💾 Guardadas {len(deduped)} props en {OUTPUT_FILE}")
    
    # 6. Sincronizar a DB
    print("🔄 Sincronizando a DB...")
    synced = 0
    for prop in deduped:
        if save_to_padim_db(prop):
            synced += 1
    if synced:
        print(f"   ✅ {synced}/{len(deduped)} sincronizadas a DB")
    else:
        print(f"   ⚠️  0/{len(deduped)} sincronizadas (psycopg2 no disponible o DB caída)")
    
    # 7. Resumen por fuente
    sources = {}
    for prop in deduped:
        s = prop.get("source", "unknown")
        if s not in sources:
            sources[s] = 0
        sources[s] += 1
    
    print(f"\n📊 Resumen por fuente:")
    for src, count in sorted(sources.items()):
        print(f"   {src:<15} {count:>4} props")
    print(f"\n{'='*50}")
    print(f"✅ Consolidación completa: {len(deduped)} propiedades en {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())