# padim/cli/scraper_manager.py
# Gestor de scrapers descargables — plugin loader estilo uBlock/Homebrew

import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

MANIFEST_URL = "https://codeberg.org/CamaradaMexicano389/mx-property-scrapers/raw/branch/main/manifest.json"
MANIFEST_FALLBACK_URL = "https://raw.githubusercontent.com/CamaradaMexicano389/mx-property-scrapers/main/manifest.json"
SCRAPER_DIR = Path.home() / ".padim" / "scrapers"


def _ensure_dir():
    SCRAPER_DIR.mkdir(parents=True, exist_ok=True)


def fetch_manifest():
    """Descarga el manifiesto de scrapers disponibles (Codeberg → GitHub → jsDelivr)."""
    urls = [MANIFEST_URL, MANIFEST_FALLBACK_URL]
    for url in urls:
        try:
            resp = urllib.request.urlopen(url, timeout=10)
            return json.loads(resp.read().decode())
        except Exception:
            continue
    print("❌ No se pudo descargar el manifiesto desde ninguna fuente.")
    return None


def verify_checksum(filepath: Path, expected_sha256: str) -> bool:
    """Verifica SHA256 del archivo descargado."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_sha256


def download_file(url: str, target: Path) -> bool:
    """Descarga un archivo desde URL a target."""
    try:
        resp = urllib.request.urlopen(url, timeout=30)
        with open(target, "wb") as f:
            f.write(resp.read())
        return True
    except Exception as e:
        print(f"   ⚠️  Falló descarga desde {url}: {e}")
        return False


def cmd_scrapers_install(args):
    """Instala un scraper desde el manifiesto."""
    _ensure_dir()
    manifest = fetch_manifest()
    if not manifest:
        return 1

    name = args.name
    scraper_info = None
    for s in manifest.get("scrapers", []):
        if s["name"] == name:
            scraper_info = s
            break

    if not scraper_info:
        disponibles = [s["name"] for s in manifest.get("scrapers", [])]
        print(f"❌ Scraper '{name}' no encontrado.")
        print(f"   Disponibles: {', '.join(disponibles)}")
        return 1

    version = scraper_info["version"]
    target = SCRAPER_DIR / f"{name}-v{version}.py"
    symlink = SCRAPER_DIR / f"{name}.py"

    # Intentar cada contentURL en orden
    for url in scraper_info.get("contentURL", []):
        print(f"📥 Descargando {name} v{version}...")
        if download_file(url, target):
            break
    else:
        print(f"❌ No se pudo descargar {name} desde ninguna fuente.")
        return 1

    # Verificar checksum
    expected = scraper_info.get("sha256", "")
    if expected and not verify_checksum(target, expected):
        target.unlink()
        print(f"❌ Checksum falló para {name}. Archivo eliminado por seguridad.")
        return 1

    # Symlink a la versión activa
    if symlink.exists() or symlink.is_symlink():
        symlink.unlink()
    symlink.symlink_to(target)

    print(f"✅ {name} v{version} instalado en ~/.padim/scrapers/{name}.py")
    return 0


def cmd_scrapers_list(args):
    """Lista scrapers instalados y disponibles."""
    _ensure_dir()
    manifest = fetch_manifest()

    if manifest:
        print("📋 Scrapers disponibles:")
        for s in manifest.get("scrapers", []):
            print(f"   • {s['name']} v{s['version']} — {s.get('description', '')}")
        print()

    print("📦 Scrapers instalados localmente:")
    installed = list(SCRAPER_DIR.glob("*.py"))
    if installed:
        for f in sorted(installed):
            print(f"   • {f.name}")
    else:
        print("   (ninguno)")

    if manifest:
        print(f"\n💡 Usa: padim scrapers install <nombre>")
    return 0


def cmd_scrapers_update(args):
    """Actualiza todos los scrapers instalados."""
    _ensure_dir()
    manifest = fetch_manifest()
    if not manifest:
        return 1

    updated = 0
    for s in manifest.get("scrapers", []):
        name = s["name"]
        symlink = SCRAPER_DIR / f"{name}.py"

        # Solo actualizar si está instalado
        if not symlink.exists():
            continue

        version = s["version"]
        target = SCRAPER_DIR / f"{name}-v{version}.py"

        # Si ya existe esa versión, saltar
        if target.exists():
            print(f"   {name} v{version} ya está actualizado")
            continue

        print(f"📥 Actualizando {name} a v{version}...")
        for url in s.get("contentURL", []):
            if download_file(url, target):
                break
        else:
            print(f"   ⚠️  No se pudo actualizar {name}")
            continue

        expected = s.get("sha256", "")
        if expected and not verify_checksum(target, expected):
            target.unlink()
            print(f"   ❌ Checksum falló para {name}")
            continue

        # Reemplazar symlink
        if symlink.exists() or symlink.is_symlink():
            symlink.unlink()
        symlink.symlink_to(target)
        updated += 1
        print(f"   ✅ {name} → v{version}")

    if updated == 0:
        print("✅ Todos los scrapers están actualizados")
    else:
        print(f"\n✅ {updated} scraper(s) actualizado(s)")
    return 0
