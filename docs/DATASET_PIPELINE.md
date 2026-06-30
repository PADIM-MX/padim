# PADIM v2.0.0 — Dataset Público y Pipeline

## Arquitectura del Pipeline de Datos

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Scraper     │ →  │ Normalizador │ →  │ Trust Engine │
│  (diario)    │    │ (schema →    │    │ (señales +   │
│              │    │  padim spec) │    │  scoring)    │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               ↓
                    ┌──────────────────────────────────┐
                    │   PostgreSQL (BACKBONE API)       │
                    │   - Datos en vivo                 │
                    │   - Query por colonia/fuente      │
                    │   - Trust scoring actualizado     │
                    └────────────┬─────────────────────┘
                                 ↓
         ┌─────────────────────────────────────────────┐
         │          GitHub Releases (semanal)           │
         │  padim-dataset-{YYYY-MM-DD}.json.gz          │
         │  SHA256 verificable en checksums.txt         │
         └────────────────────┬────────────────────────┘
                              ↓
         ┌─────────────────────────────────────────────┐
         │                IPFS (inmutable)              │
         │  CID: Qm... (cambiante cada release)         │
         │  Pins: Pinata + Filebase + nodo local         │
         │  Proovedor: ipfs.io/ipfs/{CID}               │
         └─────────────────────────────────────────────┘
```

## Opciones de Base de Datos Comunitaria

### Opción A: GitHub Releases (✅ Elegida como Default)

**Qué es:** Cada release semanal genera un `padim-dataset-{fecha}.json.gz`

**Ventajas:**
- ✅ Sin infraestructura nueva (ya usamos GitHub)
- ✅ Descargable por cualquiera sin API key
- ✅ Versionado (cada release es un checkpoint histórico)
- ✅ SHA256 verificable

**Desventajas:**
- ❌ Sin query en vivo (hay que descargar todo y filtrar localmente)
- ❌ Sin actualización en tiempo real

**Implementación:** YA está en `.github/workflows/ci.yml` — job `daily-scrape`

### Opción B: IPFS (Recomendada como Respaldo)

**Qué es:** Cada release se pinne a IPFS. El CID es la prueba de integridad.

**Cómo se implementa:**

```yaml
# En CI, después de generar el dataset:
- name: Upload to IPFS
  uses: aquiladev/ipfs-action@v1
  with:
    path: datasets/padim-dataset-daily.json
    pin: true
    service: pinata
    pinata_api_key: ${{ secrets.PINATA_API_KEY }}
    pinata_secret_key: ${{ secrets.PINATA_SECRET }}
```

**Acceso público:**
```
https://ipfs.io/ipfs/{CID}
https://gateway.pinata.cloud/ipfs/{CID}
```

### Opción C: PostgreSQL + API REST (Para BACKBONE)

**Qué es:** La API de BACKBONE expone los datos con SLA 99.9%

**Endpoints que YA existen en el CLI:**
- `GET /v1/properties?colony=X&min_trust=0.5` — Búsqueda
- `GET /v1/market/{colony}` — Estadísticas de colonia
- `GET /v1/trust/{property_id}` — Trust scoring detallado
- `GET /v1/stats` — Métricas globales
- `GET /v1/sources` — Estado de fuentes

## Formato del Dataset

```json
{
  "version": "2.0.0",
  "generated_at": "2026-07-01T06:00:00Z",
  "total_properties": 1247,
  "sources": ["vivanuncios", "inmuebles24"],
  "properties": [
    {
      "source": "vivanuncios",
      "source_id": "vv-123456",
      "title": "Departamento en Del Valle",
      "price": 4500000,
      "currency": "MXN",
      "colony": "Del Valle",
      "municipality": "Benito Juárez",
      "state": "CDMX",
      "property_type": "departamento",
      "business_type": "venta",
      "trust_score": 0.82,
      "is_relevant": true,
      "is_suspicious": false,
      "signals": ["listing_active"],
      "scraped_at": "2026-07-01T05:30:00Z"
    }
  ]
}
```

## Frecuencia de Actualización

| Canal | Frecuencia | Método |
|-------|-----------|--------|
| API (BACKBONE) | Tiempo real | PostgreSQL + FastAPI |
| GitHub Releases | Diaria (6am) | GitHub Actions |
| IPFS | Semanal | CI + Pinata |
| CSV descargable | Semanal | GitHub Actions |
