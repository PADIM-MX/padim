# PADIM — CLI Entry Point (prototype)

import argparse
import json
import sys
import os

# En desarrollo real, esto importará conectores modulares
# Por ahora es un placeholder funcional

def cmd_scrape(args):
    """Scrapea propiedades de una fuente."""
    print("⚠️  Los conectores de scraping se distribuyen por separado.")
    print("")
    print("   PADIM solo distribuye el estándar, schema y herramientas de validación.")
    print("   Los scrapers funcionales viven en un repositorio independiente:")
    print("")
    print(f"      https://github.com/Trogloautoegocrata/mx-property-scrapers")
    print("")
    print("   Para usar scraping, clona ese repositorio:")
    print("")
    print("      git clone https://github.com/Trogloautoegocrata/mx-property-scrapers")
    print("      cd mx-property-scrapers")
    print("      python3 scrape_vivanuncios.py")
    print("")
    print("   📖 Más información en el README del proyecto.")
    return 0

def cmd_validate(args):
    """Valida un archivo JSON contra el schema PADIM."""
    print(f"🔍 Validando {args.file} contra schema v1.0...")
    try:
        import jsonschema
        schema_path = os.path.join(os.path.dirname(__file__), "..", "spec", "schema.json")
        with open(args.file) as f:
            data = json.load(f)
        with open(schema_path) as f:
            schema = json.load(f)
        if isinstance(data, list):
            for i, item in enumerate(data):
                jsonschema.validate(item, schema)
            print(f"   ✅ {len(data)} propiedades válidas")
        else:
            jsonschema.validate(data, schema)
            print("   ✅ Válido")
        return 0
    except ImportError:
        print("   ⚠️ jsonschema no instalado. Instala con: pip install jsonschema")
        return 1
    except Exception as e:
        print(f"   ❌ {e}")
        return 1

def cmd_quality(args):
    """Calcula trust score para datos en archivo."""
    print(f"🧠 Calculando trust score para {args.file}...")
    try:
        from padim.engine.trust_engine import TrustEngine
        with open(args.file) as f:
            data = json.load(f)
        engine = TrustEngine()
        items = data if isinstance(data, list) else [data]
        for item in items:
            result = engine.analyze(
                property_id=item.get("source_id", "unknown"),
                source=item.get("source", "unknown"),
                title=item.get("title", ""),
                description=item.get("description", ""),
                price=item.get("price", 0),
            )
            item["trust_score"] = result.get("trust_score", 0.5)
            item["quality_grade"] = result.get("quality_grade", "FAIR")
        print(f"   ✅ Trust scores calculados para {len(items)} propiedades")
        with open(args.file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return 0
    except Exception as e:
        print(f"   ❌ {e}")
        return 1

def cmd_serve(args):
    """Sirve una API local con los datos."""
    print(f"🌐 Sirviendo API en http://localhost:{args.port}")
    print("   (Servidor no implementado en esta versión)")
    return 0

def main():
    parser = argparse.ArgumentParser(description="PADIM — Protocolo Abierto de Datos Inmobiliarios de México")
    sub = parser.add_subparsers(dest="command")
    
    p_scrape = sub.add_parser("scrape", help="Scrapea propiedades")
    p_scrape.add_argument("source", choices=["vivanuncios", "easybroker"])
    p_scrape.add_argument("--colony", "-c", default="")
    p_scrape.add_argument("--output", "-o", default="padim_data.json")
    
    p_val = sub.add_parser("validate", help="Valida datos contra schema")
    p_val.add_argument("file")
    
    p_qual = sub.add_parser("quality", help="Calcula trust score")
    p_qual.add_argument("file")
    
    p_serve = sub.add_parser("serve", help="Sirve API local")
    p_serve.add_argument("--port", "-p", type=int, default=8080)
    
    args = parser.parse_args()
    
    commands = {
        "scrape": cmd_scrape,
        "validate": cmd_validate,
        "quality": cmd_quality,
        "serve": cmd_serve,
    }
    
    if args.command in commands:
        return commands[args.command](args)
    
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
