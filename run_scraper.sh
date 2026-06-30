#!/usr/bin/env bash
# PADIM Scraper — Cron Wrapper
# Ejecuta el scraper con el venv correcto y la API key de OpenRouter
set -e

cd /home/polaris/workspace/projects/PADIM-scraper

# Activar venv
source /home/polaris/workspace/.venv-scrapling-test/bin/activate

# Exportar API key de OpenRouter (desde el entorno de Hermes si existe)
if [ -z "$OPENROUTER_API_KEY" ]; then
  # Intentar desde config de Hermes
  HERMES_KEY=$(grep -A1 'openrouter:' /home/polaris/.hermes/profiles/omegabridge/config.yaml 2>/dev/null | grep 'api_key' | awk '{print $2}')
  if [ -n "$HERMES_KEY" ]; then
    export OPENROUTER_API_KEY="$HERMES_KEY"
  fi
fi

# Ejecutar scraper
python3 scraper_padim.py 2>&1

echo ""
echo "=== Scraper completado: $(date) ==="
