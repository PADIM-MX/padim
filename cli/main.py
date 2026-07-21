# PADIM — CLI Entry Point (prototype)

import argparse
import json
import sys
import os
from pathlib import Path

from padim.cli.scraper_manager import (
    cmd_scrapers_install,
    cmd_scrapers_list,
    cmd_scrapers_update,
    cmd_scrapers_verify,
    SCRAPER_DIR,
)


def cmd_scrape(args):
    """Ejecuta un scraper instalado localmente."""
    source = args.source
    scraper_path = SCRAPER_DIR / f"{source}.py"

    if not scraper_path.exists():
        print(f"⚠️  Scraper '{source}' no está instalado.")
        print(f"")
        print(f"   Para instalar:")
        print(f"      padim scrapers install {source}")
        print(f"")
        print(f"   O lista los disponibles:")
        print(f"      padim scrapers list")
        return 1

    # Agregar SCRAPER_DIR al path y ejecutar
    sys.path.insert(0, str(SCRAPER_DIR))
    module_name = f"{source}"

    try:
        # Intentar importar como módulo
        import importlib
        mod = importlib.import_module(module_name)

        if hasattr(mod, "run"):
            result = mod.run(colony=args.colony, output=args.output)
            return 0 if result else 1
        elif hasattr(mod, "main"):
            mod.main()
            return 0
        else:
            print(f"❌ El scraper '{source}' no tiene función run() ni main().")
            return 1
    except Exception as e:
        print(f"❌ Error al ejecutar {source}: {e}")
        return 1


def cmd_scrapers(args):
    """Gestión de scrapers descargables."""
    if args.scrapers_action == "install":
        return cmd_scrapers_install(args)
    elif args.scrapers_action == "list":
        return cmd_scrapers_list(args)
    elif args.scrapers_action == "update":
        return cmd_scrapers_update(args)
    elif args.scrapers_action == "verify":
        return cmd_scrapers_verify(args)
    return 1


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

    # scrape
    p_scrape = sub.add_parser("scrape", help="Ejecuta un scraper instalado")
    p_scrape.add_argument("source", help="Nombre del scraper (ej: inmuebles24, vivanuncios)")
    p_scrape.add_argument("--colony", "-c", default="")
    p_scrape.add_argument("--output", "-o", default="padim_data.json")

    # scrapers (gestión)
    p_scrapers = sub.add_parser("scrapers", help="Gestiona scrapers descargables")
    p_scrapers_sub = p_scrapers.add_subparsers(dest="scrapers_action")

    p_install = p_scrapers_sub.add_parser("install", help="Instala un scraper")
    p_install.add_argument("name", help="Nombre del scraper a instalar")

    p_list = p_scrapers_sub.add_parser("list", help="Lista scrapers disponibles e instalados")

    p_update = p_scrapers_sub.add_parser("update", help="Actualiza scrapers instalados")

    p_verify = p_scrapers_sub.add_parser("verify", help="Verifica seguridad de un scraper antes de publicarlo")
    p_verify.add_argument("file", help="Ruta al archivo .py del scraper")

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

    if args.command == "scrapers":
        return cmd_scrapers(args)
    elif args.command in commands:
        return commands[args.command](args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
