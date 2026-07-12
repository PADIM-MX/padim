"""
PADIM — CLI Entry Point v2.0.0
CLI real con scrapers funcionales + API server.
"""
import argparse
import json
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


# ── SCRAPER ENGINE ──────────────────────────────────────────────

def load_schema() -> dict:
    """Carga el schema PADIM desde spec/."""
    schema_path = Path(__file__).parent.parent / "spec" / "schema.json"
    if schema_path.exists():
        import jsonschema
        with open(schema_path) as f:
            return json.load(f)
    return {}


def validate_against_schema(data: list | dict) -> tuple[bool, list]:
    """Valida datos contra el schema PADIM. Retorna (valido, errores)."""
    try:
        import jsonschema
        schema = load_schema()
        if not schema:
            return True, []
        items = data if isinstance(data, list) else [data]
        errors = []
        for i, item in enumerate(items):
            try:
                jsonschema.validate(item, schema)
            except jsonschema.ValidationError as e:
                errors.append(f"Item {i}: {e.message}")
        return len(errors) == 0, errors
    except ImportError:
        return True, []


def run_trust_engine(data: list | dict) -> list | dict:
    """Ejecuta Trust Engine sobre los datos."""
    try:
        from padim.engine.trust_engine import TrustEngine
        engine = TrustEngine()
        items = data if isinstance(data, list) else [data]
        results = []
        for item in items:
            # Ejecutar sync (el método analyze es sync en v2)
            try:
                result = engine.analyze(
                    property_id=item.get("source_id", str(item.get("fingerprint", "unknown"))),
                    source=item.get("source", item.get("portal", "unknown")),
                    title=item.get("title", item.get("titulo", "")),
                    description=item.get("description", item.get("descripcion", "")),
                    price=item.get("price", item.get("precio", 0)),
                    price_m2=item.get("price_m2", None),
                    property_type=item.get("property_type", item.get("tipo_inmueble", "otro")),
                    last_updated=item.get("last_updated", None),
                    days_on_market=None,
                    price_changes=0,
                    source_count=1,
                    colony=item.get("colony", item.get("colonia", "")),
                    municipality=item.get("municipality", ""),
                    agent_name=item.get("agent_name", None),
                    agent_properties_count=0,
                )
                item["trust_score"] = round(result.trust_score, 2)
                item["is_relevant"] = result.is_relevant
                item["is_suspicious"] = result.is_suspicious
                item["signals"] = [s.type.value for s in result.signals]
            except Exception as e:
                item["trust_score"] = 0.5
                item["trust_error"] = str(e)
            results.append(item)
        return results if isinstance(data, list) else results[0]
    except Exception as e:
        return data


# ── SCRAPERS REALES ──────────────────────────────────────────────

SCRAPER_SOURCES = {
    "vivanuncios": {
        "name": "Vivanuncios",
        "url": "https://www.vivanuncios.com.mx",
    },
    "inmuebles24": {
        "name": "Inmuebles24",
        "url": "https://www.inmuebles24.com",
    },
    "propiedades": {
        "name": "Propiedades.com",
        "url": "https://www.propiedades.com",
    },
    "easybroker": {
        "name": "EasyBroker",
        "url": "https://www.easybroker.com",
    },
    "lamudi": {
        "name": "Lamudi",
        "url": "https://www.lamudi.com.mx",
    },
}


def scrape_source(source: str, colony: str, output: str) -> int:
    """
    Ejecuta scraper real delegando a:
    1) PADIMScraper nativo (tiene conectores Inmuebles24, Vivanuncios, Lamudi funcionales)
    2) Scraper dedicado en ~/.padim/scrapers/{source}.py
    3) Engine universal (httpx + parsers)
    """
    data = None

    # 1) Intentar PADIMScraper nativo
    try:
        from padim.scrapers.scraper_padim import PADIMScraper
        padim_scraper = PADIMScraper()
        data = padim_scraper.scrape(portal=source)
        if data:
            print(f"  ✅ Scraper nativo PADIM: {len(data)} propiedades")
    except Exception as e:
        print(f"  ⚠️  Scraper nativo no disponible: {e}")

    # 2) Scraper dedicado en ~/.padim/scrapers/
    if not data:
        scrapers_dir = Path.home() / ".padim" / "scrapers"
        dedicated = scrapers_dir / f"{source}.py"
        if dedicated.exists():
            sys.path.insert(0, str(scrapers_dir))
            import importlib
            mod = importlib.import_module(source)
            data = mod.scrape(colony=colony)

    # 3) Engine universal
    if not data:
        data = _universal_scrape(source, colony)

    if not data:
        print(f"  ⚠️  No se encontraron propiedades para '{colony}' en {source}")
        return 1

    # Normalizar
    normalized = [_normalize(item, source) for item in data]

    # Validar contra schema
    valid, errors = validate_against_schema(normalized)
    if not valid:
        print(f"  ⚠️  {len(errors)} errores de validación (continuando de todas formas):")
        for e in errors[:3]:
            print(f"       • {e}")

    # Trust Engine
    print(f"  🧠 Calculando trust scores...")
    scored = run_trust_engine(normalized)

    # Guardar
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(scored, f, indent=2, ensure_ascii=False)

    total = len(scored)
    real = sum(1 for p in scored if p.get("is_relevant", True) and p.get("trust_score", 0.5) >= 0.3)
    ghosts = sum(1 for p in scored if not p.get("is_relevant", True))
    suspicious = sum(1 for p in scored if p.get("is_suspicious", False))

    print(f"  ✅ {total} propiedades → {real} reales, {ghosts} fantasma, {suspicious} sospechosas")
    print(f"  📁 Guardado en {output_path}")
    return 0


def _universal_scrape(source: str, colony: str) -> list:
    """Scraper universal. Intenta curl_cffi primero (para Cloudflare), fallback httpx."""
    import re

    urls = {
        "vivanuncios": f"https://www.vivanuncios.com.mx/s-venta-inmuebles/{colony.lower().replace(' ','-').replace('+','-')}/v1c1097p1",
        "inmuebles24": f"https://www.inmuebles24.com/{colony.lower().replace(' ','-').replace('+','-')}.html",
        "propiedades": f"https://www.propiedades.com/{colony.lower().replace(' ','-').replace('+','-')}.html",
        "easybroker": f"https://www.easybroker.com/mx/propiedades/{colony.lower().replace(' ','-').replace('+','-')}",
    }

    url = urls.get(source)
    if not url:
        print(f"  ❌ Fuente '{source}' no soportada en modo universal")
        return []

    html = None

    # Estrategia 1: curl_cffi (pasa Cloudflare)
    try:
        from curl_cffi import requests as curl_requests
        print(f"  📡 Consultando {source} (curl_cffi)...")
        resp = curl_requests.get(url, impersonate="chrome110", timeout=30)
        if resp.status_code == 200:
            html = resp.text
            print(f"  ✅ curl_cffi OK")
    except ImportError:
        pass
    except Exception as e:
        print(f"  ⚠️  curl_cffi falló: {e}")

    # Estrategia 2: httpx (fallback si curl_cffi no está o falló)
    if not html:
        try:
            import httpx
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
            }
            print(f"  📡 Consultando {source} (httpx fallback)...")
            resp = httpx.get(url, headers=headers, follow_redirects=True, timeout=30)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            print(f"  ❌ Error HTTP: {e}")
            return []

    return _parse_listings(html, source, url, colony)


def _map_vivanuncios_type(real_estate_type) -> str:
    """Mapea tipos de Vivanuncios al schema PADIM."""
    if isinstance(real_estate_type, dict):
        name = real_estate_type.get("name", "")
    else:
        name = str(real_estate_type)
    mapping = {
        "Casa": "casa", "Casas": "casa",
        "Departamento": "departamento", "Departamentos": "departamento",
        "Terreno": "terreno", "Terrenos": "terreno",
        "Local": "local", "Locales comerciales": "local",
        "Oficina": "oficina", "Oficinas": "oficina",
        "Bodega": "bodega", "Bodegas": "bodega",
        "Nave industrial": "nave_industrial",
        "Edificio": "edificio",
        "Desarrollo": "otro",
    }
    return mapping.get(name, "otro")


def _map_operation(operation_name: str) -> str:
    """Mapea tipo de operación."""
    mapping = {
        "Venta": "venta",
        "Renta": "renta",
        "Traspaso": "traspaso",
    }
    return mapping.get(operation_name, "venta")


def _parse_listings(html: str, source: str, base_url: str, colony: str) -> list:
    """Parser universal de listings desde HTML."""
    import re
    import json as _json

    listings = []

    # ── Estrategia 1: PRELOADED_STATE (Vivanuncios con React) ──
    m = re.search(
        r'<script id="preloadedData">\s*window\.__PRELOADED_STATE__\s*=\s*(\{.+?\});',
        html, re.DOTALL
    )
    if m:
        try:
            data = _json.loads(m.group(1))
            postings = data.get("listStore", {}).get("listPostings", [])
            for item in postings:
                price_info = item.get("priceOperationTypes", [{}])[0]
                prices = price_info.get("prices", [{}])
                amount = prices[0].get("amount", 0) if prices else 0
                currency = prices[0].get("currency", "MN") if prices else "MN"

                listing = {
                    "source": source,
                    "source_id": str(item.get("postingId", "")),
                    "source_url": base_url,
                    "title": item.get("title", ""),
                    "description": item.get("generatedTitle", ""),
                    "property_type": _map_vivanuncios_type(item.get("realEstateType", "")),
                    "business_type": _map_operation(price_info.get("operationType", {}).get("name", "Venta")),
                    "price": int(amount) if amount else 0,
                    "currency": "MXN" if currency == "MN" else currency,
                    "colony": colony.title(),
                    "images": [],
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "agent_name": item.get("publisher", {}).get("name") if isinstance(item.get("publisher"), dict) else None,
                }
                if listing["price"] > 1000 and listing["title"]:
                    listings.append(listing)

            if listings:
                return listings
        except Exception:
            pass

    # ── Estrategia 2: JSON-LD ──
    jsonlds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    for j in jsonlds:
        try:
            data = _json.loads(j)
            items = data.get("@graph", [data]) if isinstance(data, dict) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                offers = item.get("offers", {}) or {}
                price_val = None
                if isinstance(offers, dict):
                    price_val = offers.get("price")
                if not price_val:
                    price_val = item.get("price")

                if price_val and float(price_val) > 10000:
                    addr = item.get("address", {}) or {}
                    geo = item.get("geo", {}) or {}
                    name = item.get("name", "")
                    desc = item.get("description", "")

                    listing = {
                        "source": source,
                        "source_id": item.get("@id", str(hash(name))),
                        "source_url": base_url,
                        "title": name,
                        "description": desc[:500] if desc else None,
                        "property_type": "otro",
                        "business_type": "venta",
                        "price": int(float(price_val)),
                        "currency": "MXN",
                        "colony": colony.title(),
                        "address": addr.get("streetAddress", ""),
                        "lat": float(geo["latitude"]) if geo.get("latitude") else None,
                        "lng": float(geo["longitude"]) if geo.get("longitude") else None,
                        "images": [],
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    }
                    listings.append(listing)
        except (_json.JSONDecodeError, ValueError, TypeError):
            pass

    # Fallback: data-atributos y regex (para listings sin JSON-LD)
    if not listings:
        # Buscar bloques de tarjetas
        cards = re.findall(
            r'<div[^>]*class="[^"]*?(?:card|property|listing|ad)[^"]*"[^>]*>'
            r'(.*?)</div>\s*</div>\s*</div>',
            html, re.DOTALL
        )
        for card_html in cards[:30]:
            # Precio
            price_match = re.search(r'(?:\$|MXN)\s*([0-9,]+)', card_html)
            if not price_match:
                continue
            price = int(price_match.group(1).replace(",", ""))

            # Titulo
            title_match = re.search(r'<h[2-4][^>]*>(.*?)</h[2-4]>', card_html, re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""

            if price < 1000:
                continue

            listing = {
                "source": source,
                "source_id": f"{source}_{hash(card_html[:100])}",
                "source_url": base_url,
                "title": re.sub(r'<[^>]+>', '', title),
                "description": None,
                "property_type": "otro",
                "business_type": "venta",
                "price": price,
                "currency": "MXN",
                "colony": colony.title(),
                "lat": None,
                "lng": None,
                "images": [],
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            }
            listings.append(listing)

    return listings


def _normalize(item: dict, source: str) -> dict:
    """Normaliza los datos scrapeados al schema PADIM estandar."""
    return {
        "source": source,
        "source_id": item.get("source_id", ""),
        "source_url": item.get("source_url", ""),
        "title": item.get("title", ""),
        "description": item.get("description") or None,
        "property_type": item.get("property_type", "otro"),
        "business_type": item.get("business_type", "venta"),
        "price": item.get("price", 0),
        "currency": item.get("currency", "MXN"),
        "price_m2": item.get("price_m2") or None,
        "m2_constructed": item.get("m2_constructed") or None,
        "m2_land": item.get("m2_land") or None,
        "bedrooms": item.get("bedrooms") or None,
        "bathrooms": item.get("bathrooms") or None,
        "parking": item.get("parking") or None,
        "address": item.get("address", ""),
        "colony": item.get("colony", ""),
        "municipality": item.get("municipality", ""),
        "state": item.get("state", ""),
        "lat": item.get("lat") or None,
        "lng": item.get("lng") or None,
        "images": item.get("images", []),
        "agent_name": item.get("agent_name") or None,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


# ── API SERVER ──────────────────────────────────────────────────

def start_server(port: int = 8080):
    """Inicia servidor FastAPI con datos de PADIM."""
    try:
        import uvicorn
        from fastapi import FastAPI, Query
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(
            title="PADIM API",
            version="2.0.0",
            description="Protocolo Abierto de Datos Inmobiliarios de México",
            docs_url="/docs",
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Cargar datos disponibles
        properties_cache = []
        # Intentar NDJSON primero (propiedades.jsonl)
        jsonl_file = Path("data/propiedades.jsonl")
        if jsonl_file.exists():
            with open(jsonl_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            properties_cache.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        # Fallback a padim_data.json
        data_file = Path("padim_data.json")
        if not properties_cache and data_file.exists():
            with open(data_file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    properties_cache = data
                else:
                    properties_cache = [data]

        @app.get("/")
        def root():
            return {
                "name": "PADIM API",
                "version": "2.0.0",
                "description": "Protocolo Abierto de Datos Inmobiliarios de México",
                "docs": "/docs",
                "endpoints": {
                    "properties": "GET /v1/properties?colony=&min_trust=&source=&business_type=",
                    "market": "GET /v1/market/{colony}",
                    "trust": "GET /v1/trust/{property_id}",
                    "sources": "GET /v1/sources",
                    "stats": "GET /v1/stats",
                },
            }

        @app.get("/v1/properties")
        def get_properties(
            colony: str = Query(None, description="Colonia a filtrar"),
            min_trust: float = Query(0.0, ge=0.0, le=1.0, description="Trust score mínimo"),
            source: str = Query(None, description="Fuente (vivanuncios, inmuebles24, etc)"),
            business_type: str = Query(None, description="venta/renta"),
            limit: int = Query(100, ge=1, le=1000),
        ):
            results = list(properties_cache)
            if colony:
                results = [p for p in results if colony.lower() in p.get("colony", "").lower()
                           or colony.lower() in p.get("colonia", "").lower()]
            if min_trust > 0:
                results = [p for p in results if p.get("trust_score", 0.5) >= min_trust]
            if source:
                results = [p for p in results if p.get("source", "") == source]
            if business_type:
                results = [p for p in results if p.get("business_type", "") == business_type]
            return {
                "total": len(results),
                "results": results[:limit],
                "query": {
                    "colony": colony,
                    "min_trust": min_trust,
                    "source": source,
                    "business_type": business_type,
                },
            }

        @app.get("/v1/market/{colony}")
        def get_market(colony: str):
            """Estadísticas de mercado para una colonia."""
            relevant = [p for p in properties_cache
                        if colony.lower().replace('-',' ') in p.get("colony", "").lower().replace('-',' ')
                        or colony.lower().replace('-',' ') in p.get("colonia", "").lower().replace('-',' ')]
            prices = [p["price"] for p in relevant if p.get("price", 0) > 0]
            if not prices:
                return {"colony": colony, "error": "Sin datos para esta colonia"}
            return {
                "colony": colony,
                "total_properties": len(relevant),
                "avg_price": sum(prices) / len(prices),
                "median_price": sorted(prices)[len(prices) // 2],
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_trust": sum(p.get("trust_score", 0.5) for p in relevant) / len(relevant),
                "suspicious": sum(1 for p in relevant if p.get("is_suspicious", False)),
                "sources": list(set(p.get("source", "unknown") for p in relevant)),
            }

        @app.get("/v1/trust/{property_id}")
        def get_trust(property_id: str):
            for p in properties_cache:
                if p.get("source_id", "") == property_id or p.get("fingerprint", "") == property_id:
                    return {
                        "property": p.get("title", ""),
                        "trust_score": p.get("trust_score", 0.5),
                        "is_relevant": p.get("is_relevant", True),
                        "is_suspicious": p.get("is_suspicious", False),
                        "signals": p.get("signals", []),
                    }
            return {"error": "Property not found", "property_id": property_id}

        @app.get("/v1/sources")
        def get_sources():
            return {"sources": list(SCRAPER_SOURCES.keys()), "details": SCRAPER_SOURCES}

        @app.get("/v1/stats")
        def get_stats():
            if not properties_cache:
                return {"status": "no_data", "message": "Ejecuta 'padim scrape' primero para cargar datos"}
            total = len(properties_cache)
            real = sum(1 for p in properties_cache if p.get("is_relevant", True))
            suspicious = sum(1 for p in properties_cache if p.get("is_suspicious", False))
            colonies = set()
            for p in properties_cache:
                col = p.get("colony", p.get("colonia", ""))
                if col:
                    colonies.add(col)
            return {
                "total_properties": total,
                "real_properties": real,
                "suspicious": suspicious,
                "colonies": sorted(colonies),
                "colony_count": len(colonies),
                "avg_trust": sum(p.get("trust_score", 0.5) for p in properties_cache) / total if total else 0,
            }

        @app.post("/v1/contributions")
        def post_contributions(body: dict):
            """Recibe propiedades de contribuidores externos."""
            from uuid import uuid4
            source_name = body.get("source", "contribucion_directa")
            items = body.get("properties", [])
            if not items:
                return {"error": "No properties in body", "accepted": 0}
            
            accepted = 0
            for item in items:
                try:
                    prop = {
                        "source": source_name,
                        "source_id": str(uuid4()),
                        "source_url": item.get("source_url", ""),
                        "title": item.get("title", item.get("property_type", "otro")),
                        "description": item.get("description", None),
                        "property_type": item.get("property_type", "otro"),
                        "business_type": item.get("business_type", "venta"),
                        "price": int(item.get("price", 0)),
                        "currency": item.get("currency", "MXN"),
                        "m2_constructed": item.get("m2_constructed", None),
                        "bedrooms": item.get("bedrooms", None),
                        "bathrooms": item.get("bathrooms", None),
                        "address": item.get("address", ""),
                        "colony": item.get("colony", ""),
                        "state": item.get("state", ""),
                        "images": item.get("images", []),
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    }
                    properties_cache.append(prop)
                    accepted += 1
                except Exception:
                    pass
            
            return {"source": source_name, "accepted": accepted, "total": len(items)}

        print(f"  🌐 PADIM API corriendo en http://0.0.0.0:{port}")
        print(f"  📚 Documentación: http://0.0.0.0:{port}/docs")
        print(f"  📡 Endpoints: /v1/properties, /v1/market/{{colony}}, /v1/stats, /v1/contributions")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

    except ImportError as e:
        print(f"  ❌ Error: {e}")
        print(f"  💡 Instala las dependencias: pip install 'padim[server]'")
        return 1
    return 0


# ── CLI COMMANDS ─────────────────────────────────────────────────

def cmd_scrape(args):
    """Scrapea propiedades de una fuente usando PADIMScraper."""
    print(f"📡 Scrapeando {args.source} para colonia: {args.colony}")
    print(f"   Output: {args.output}")
    
    try:
        from padim.scrapers.scraper_padim import PADIMScraper
        scraper = PADIMScraper()
        propiedades = scraper.scrape(portal=args.source)
    except ImportError as e:
        print(f"  ❌ Error importando PADIMScraper: {e}")
        print(f"  💡 Asegúrate de tener instaladas las dependencias: scrapling, yaml")
        return 1
    except Exception as e:
        print(f"  ❌ Error durante scraping: {e}")
        return 1

    if not propiedades:
        print(f"  ⚠️  No se encontraron propiedades para '{args.colony}' en {args.source}")
        return 1

    # Normalizar a schema PADIM
    def _normalize_to_schema(prop: dict) -> dict:
        return {
            "source": args.source,
            "source_id": prop.get("fingerprint", prop.get("url", "")),
            "source_url": prop.get("url", ""),
            "title": prop.get("titulo", ""),
            "description": prop.get("descripcion") or None,
            "property_type": prop.get("tipo_inmueble", "otro"),
            "business_type": prop.get("tipo_operacion", "venta"),
            "price": prop.get("precio_mxn", prop.get("precio", 0)),
            "currency": "MXN",
            "price_m2": None,
            "m2_constructed": prop.get("metros_cuadrados") or None,
            "m2_land": prop.get("metros_terreno") or None,
            "bedrooms": prop.get("recamaras") or None,
            "bathrooms": prop.get("banos") or None,
            "parking": None,
            "address": prop.get("direccion", ""),
            "colony": prop.get("colonia", ""),
            "municipality": "",
            "state": prop.get("estado", ""),
            "lat": prop.get("latitud") or None,
            "lng": prop.get("longitud") or None,
            "images": prop.get("fotos", []),
            "agent_name": None,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    normalized = [_normalize_to_schema(p) for p in propiedades]

    # Validar contra schema
    valid, errors = validate_against_schema(normalized)
    if not valid:
        print(f"  ⚠️  {len(errors)} errores de validación (continuando de todas formas):")
        for e in errors[:3]:
            print(f"       • {e}")

    # Trust Engine
    print(f"  🧠 Calculando trust scores...")
    scored = run_trust_engine(normalized)

    # Guardar
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(scored, f, indent=2, ensure_ascii=False)

    total = len(scored)
    real = sum(1 for p in scored if p.get("is_relevant", True) and p.get("trust_score", 0.5) >= 0.3)
    ghosts = sum(1 for p in scored if not p.get("is_relevant", True))
    suspicious = sum(1 for p in scored if p.get("is_suspicious", False))

    print(f"  ✅ {total} propiedades → {real} reales, {ghosts} fantasma, {suspicious} sospechosas")
    print(f"  📁 Guardado en {output_path}")
    return 0


def cmd_validate(args):
    """Valida un archivo JSON contra el schema PADIM."""
    print(f"🔍 Validando {args.file} contra schema v2.0...")
    try:
        with open(args.file) as f:
            raw = f.read().strip()

        # Intentar como JSON array primero
        if raw.startswith("["):
            data = json.loads(raw)
        # Intentar como NDJSON (objeto por linea)
        elif raw.startswith("{"):
            lines = [l.strip() for l in raw.split("\n") if l.strip()]
            data = []
            for line in lines:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            if not data:
                print("   No se pudo parsear ningun objeto del archivo")
                return 1
            print(f"   Detectado formato NDJSON ({len(lines)} lineas, {len(data)} validas)")
        else:
            print("   Formato no reconocido")
            return 1

        valid, errors = validate_against_schema(data)
        if valid:
            items = data if isinstance(data, list) else [data]
            print(f"   OK {len(items)} propiedades validas")
            return 0
        else:
            print(f"   ERROR {len(errors)} errores:")
            for e in errors:
                print(f"      * {e}")
            return 1
    except FileNotFoundError:
        print(f"   Archivo no encontrado: {args.file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"   JSON invalido: {e}")
        return 1


def cmd_quality(args):
    """Calcula trust score para datos en archivo."""
    print(f"🧠 Calculando trust score para {args.file}...")
    try:
        with open(args.file) as f:
            data = json.load(f)
        scored = run_trust_engine(data)
        with open(args.file, "w") as f:
            json.dump(scored, f, indent=2, ensure_ascii=False)
        items = scored if isinstance(scored, list) else [scored]
        avg_trust = sum(p.get("trust_score", 0.5) for p in items) / len(items)
        print(f"   ✅ Trust scores calculados para {len(items)} propiedades")
        print(f"   📊 Trust promedio: {avg_trust:.2f}")
        print(f"   👻 Fantasmas: {sum(1 for p in items if not p.get('is_relevant', True))}")
        print(f"   🚨 Sospechosas: {sum(1 for p in items if p.get('is_suspicious', False))}")
        return 0
    except Exception as e:
        print(f"   ❌ {e}")
        return 1


def cmd_serve(args):
    """Sirve una API local con los datos. Si no hay datos, intenta scrapear primero."""
    data_file = Path("padim_data.json")
    if not data_file.exists():
        print("  📡 No se encontraron datos locales. Intenta ejecutar 'padim scrape' primero.")
    return start_server(port=args.port)


def cmd_sources(args):
    """Lista las fuentes de datos disponibles."""
    print("📡 Fuentes disponibles:")
    for key, info in SCRAPER_SOURCES.items():
        status = "✅" if Path.home().joinpath(".padim/scrapers", f"{key}.py").exists() else "⬜"
        print(f"   {status} {info['name']:<15} ({key})")
    print()
    print("💡 Instala scrapers dedicados en ~/.padim/scrapers/")
    print("   para mejor parsing. El modo universal funciona sin ellos.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="PADIM — Protocolo Abierto de Datos Inmobiliarios de México v2.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  padim scrape vivanuncios --colony "Del Valle" --output delvalle.json
  padim scrape inmuebles24 --colony "Condesa" --output condesa.json
  padim validate delvalle.json
  padim quality delvalle.json
  padim serve --port 8080
  padim sources
        """,
    )
    sub = parser.add_subparsers(dest="command")

    p_scrape = sub.add_parser("scrape", help="Scrapea propiedades de una fuente")
    p_scrape.add_argument("source", choices=list(SCRAPER_SOURCES.keys()),
                          help="Fuente de datos")
    p_scrape.add_argument("--colony", "-c", default="", required=True,
                          help="Colonia a scrapear")
    p_scrape.add_argument("--output", "-o", default="padim_data.json",
                          help="Archivo de salida")

    p_val = sub.add_parser("validate", help="Valida datos contra schema PADIM")
    p_val.add_argument("file", help="Archivo JSON a validar")

    p_qual = sub.add_parser("quality", help="Calcula trust score con Trust Engine")
    p_qual.add_argument("file", help="Archivo JSON a analizar")

    p_serve = sub.add_parser("serve", help="Sirve API REST local")
    p_serve.add_argument("--port", "-p", type=int, default=8080,
                         help="Puerto del servidor")

    p_sources = sub.add_parser("sources", help="Lista fuentes disponibles")

    args = parser.parse_args()

    commands = {
        "scrape": cmd_scrape,
        "validate": cmd_validate,
        "quality": cmd_quality,
        "serve": cmd_serve,
        "sources": cmd_sources,
    }

    if args.command in commands:
        return commands[args.command](args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
