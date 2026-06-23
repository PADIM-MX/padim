# 🏠 PADIM — Protocolo Abierto de Datos Inmobiliarios de México

**El estándar abierto para datos inmobiliarios de México. Herramientas libres. Datos de todos.**

---

## ⚡ Quick Start

```bash
pip install padim

# Scrapea propiedades de una colonia
padim scrape vivanuncios --colonia "Del Valle" --output delvalle.json

# Valida la calidad de los datos
padim validate delvalle.json

# Calcula trust score
padim quality delvalle.json

# Sirve una API local con los datos
padim serve delvalle.json --port 8080
```

---

## 🧱 Estructura del Repositorio

```
padim/
├── cli/              # Interfaz de línea de comandos
├── connectors/       # Conectores modulares (cada uno con su mantenedor)
│   ├── vivanuncios/  # Scraper Vivanuncios (curl_cffi)
│   ├── easybroker/   # Conector EasyBroker API
│   ├── inegi/        # Datos INEGI (públicos)
│   ├── catastro/     # Datos catastrales (cuando estén disponibles)
│   └── shf/          # Datos SHF de transacciones reales
├── engine/           # Trust Engine + Quality Scoring (lógica pura, sin DB)
├── spec/             # El estándar: schema, API spec, documentación
├── tests/            # Tests
├── docs/             # Documentación
└── scripts/          # Utilidades de despliegue
```

---

## 📐 El Estándar (v1.0)

El schema de datos PADIM está en `spec/schema.json`. Es un formato JSON/GeoJSON para representar propiedades inmobiliarias mexicanas.

**Campos principales:**
- `source`, `source_id`, `source_url` — Procedencia
- `title`, `description`, `property_type`, `business_type` — Descripción
- `price`, `currency`, `price_m2` — Precio
- `m2_constructed`, `m2_land`, `bedrooms`, `bathrooms`, `parking` — Dimensiones
- `address`, `colony`, `municipality`, `state`, `lat`, `lng` — Ubicación
- `features`, `amenities`, `condition`, `images` — Características
- `agent_name`, `agent_agency`, `agent_phone`, `agent_email` — Agente
- `trust_score`, `freshness_score`, `quality_grade` — Calidad
- `scraped_at`, `last_updated`, `created_at` — Tiempo

Ver `spec/README.md` para la especificación completa.

---

## 🧠 Trust Engine

El Trust Engine es un conjunto de detectores que evalúan la confiabilidad de cada propiedad:

| Detector | ¿Qué detecta? | Impacto |
|----------|--------------|---------|
| GhostListingDetector | Propiedades que ya no existen (>90d sin cambios) | -0.5 a -1.0 |
| PriceAnomalyDetector | Precios irrealmente bajos o altos | -0.7 a -1.0 |
| FraudDetector | Keywords fraudulentas + precio anómalo | -0.6 a -0.9 |
| VendorBehaviorDetector | Agentes que dejan anuncios viejos para generar llamadas | -0.3 a -0.6 |

**No necesita base de datos.** Es lógica pura. Corre en tu máquina.

---

## 🤝 ¿Cómo contribuir?

| Quiero... | Hago... |
|-----------|---------|
| Usar los datos | `pip install padim` y `padim scrape` |
| Contribuir datos | Corro `padim scrape` desde mi máquina y los datos se validan automáticamente |
| Mantener un conector | Adopto un conector en `connectors/` y lo mantengo actualizado |
| Mejorar el Trust Engine | Abro un PR en `engine/` |
| Reportar un bug | Abro un issue |
| Usar el estándar en mi empresa | Adopto `spec/schema.json` como formato interno |

---

## 🔗 BACKBONE — La Implementación Enterprise

BACKBONE (`https://back-bone.dev`) es la implementación de referencia del protocolo PADIM en su versión enterprise: datos curados, SLA 99.9%, trust scoring completo, AVM ML, webhooks en tiempo real, integración con CRMs (GHL, Salesforce, HubSpot).

**PADIM es gratis. BACKBONE cobra por la confianza y el servicio.**

---

## 📜 Licencia

- **Estándar (spec/)**: CC0 1.0 Universal (Dominio Público)
- **Herramientas (cli/, connectors/, engine/)**: MIT License
- **Datos contribuidos**: ODbL (Open Database License) — requiere atribución

Ver `LICENSE` para detalles.

---

## 🌐 Enlaces

- **Landing**: https://PADIM.enmexico.casa
- **BACKBONE**: https://back-bone.dev
- **Documentación**: https://PADIM.enmexico.casa/docs
- **Discord**: [Por definir]
- **Twitter/X**: [Por definir]

---

*"Los datos inmobiliarios de México no deberían estar atrapados."*
