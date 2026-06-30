# PADIM Scraper

Scraping inmobiliario MX con Scrapling + IA (Ring-2.6-1T opcional).

## Stack

- **Scrapling 0.4.9** — Bypass Cloudflare Turnstile, adaptive scraping
- **StealthyFetcher** — Para Inmuebles24 y Vivanuncios (con `solve_cloudflare=True`)
- **DynamicFetcher** — Para Lamudi (Chromium headless)
- **Ring-2.6-1T** — (opcional) Extracción de datos vía IA

## Portales Soportados

| Portal | Status | Fetcher | Cloudflare |
|--------|--------|---------|------------|
| Inmuebles24 | ✅ | StealthyFetcher | ✅ Bypass |
| Vivanuncios | ✅ | StealthyFetcher | ✅ Bypass |
| Lamudi | ✅ | DynamicFetcher | Sin CF |

## Instalación

```bash
cd projects/PADIM-scraper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m patchright install chromium
```

## Uso

```bash
source .venv/bin/activate
python3 scraper_padim.py
```

## Output

`data/propiedades.jsonl` — una propiedad por línea en JSON.

## Deduplicación

- **Intra-portal**: SHA256 fingerprint (titulo + precio + metros + recamaras + direccion)
- **Inter-portal**: RapidFuzz (precio ±10% + colonia fuzzy match)

## Costos (500K propiedades)

| Componente | Costo/mes |
|------------|-----------|
| Scrapling | $0 |
| VPS Hetzner CX42 | $15 |
| Ring-2.6-1T (IA) | ~$269 |
| **Total** | **~$304** |
