"""
PADIM Scrapers — Módulo de conectores inmobiliarios MX.

⚠️  AVISO DE MIGRACIÓN (v2.1.0)
Este módulo se migrará al repositorio independiente:
    https://github.com/PADIM-MX/padim-scrapers

El código permanece aquí para compatibilidad, pero se eliminará
en PADIM v3.0.0. Para nuevos proyectos, usa:
    pip install padim-scrapers

Exporta:
- PADIMScraper: clase orquestadora con método scrape()
- Inmuebles24Connector, VivanunciosConnector, LamudiConnector
- Funciones utilitarias (fingerprint, validar_calidad, detectar_moneda, etc.)
"""

from padim.scrapers.scraper_padim import PADIMScraper

__all__ = ["PADIMScraper"]
__version__ = "2.0.0"
