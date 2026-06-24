# 🏠 PADIM — Protocolo Abierto de Datos Inmobiliarios de México

**Deja de perder 6 meses construyendo la misma infraestructura de datos que todos los demás. Empieza a construir productos que tus clientes realmente necesitan.**

---

## ⚡ En 5 minutos tienes datos de cualquier colonia

```bash
pip install padim

# Datos de una colonia en segundos
padim scrape vivanuncios --colonia "Del Valle" --output delvalle.json

# Valida que los datos sean correctos
padim validate delvalle.json

# Calcula qué tan confiables son
padim quality delvalle.json

# Sirve tu propia API local
padim serve --port 8080
```

**Sin servidores. Sin suscripciones. Sin esperar a que nadie te dé permiso.**

---

## ⚠️ Aviso Legal

PADIM es un proyecto de código abierto que proporciona **especificaciones y herramientas** para acceder a datos inmobiliarios públicos.

**Al usar este proyecto, aceptas que:**
- Eres el único responsable del cumplimiento legal en tu jurisdicción
- Los conectores funcionales se distribuyen por canales **descentralizados** (ver sección "Scrapers Funcionales" abajo)
- Este proyecto no almacena, procesa ni distribuye datos personales
- Los datos obtenidos deben usarse de acuerdo con los términos de servicio de cada fuente

**No somos abogados. Si tienes dudas legales, consulta a uno.**

---

## 🏗️ ¿Qué problema resuelve PADIM?

**El mercado inmobiliario mexicano está roto.** Treinta plataformas tienen los datos atrapados. Ninguna comparte. Los agentes dejan anuncios viejos para generar llamadas. Los fraudes se multiplican. Las startups gastan 6 meses scrapeando antes de escribir su producto.

PADIM es el **lenguaje común** que rompe ese cerco.

**Con PADIM puedes:**
- ✅ Obtener datos de cualquier colonia de México en minutos
- ✅ Saber qué propiedades son reales y cuáles son fantasmas
- ✅ Calcular el precio real de mercado de una zona
- ✅ Construir productos inmobiliarios sin empezar de cero
- ✅ Integrar datos de múltiples fuentes en un solo formato

**No vendemos datos. Te devolvemos el control sobre ellos.**

---

## 📦 Scrapers Funcionales — Estrategia de 3 Capas

Los conectores funcionales para scraping NO están en este repositorio. Se distribuyen a través de **3 canales independientes** diseñados para ser resistentes a cualquier intento de censura o eliminación:

### Capa 1: Radicle (Red P2P) — REPOSITORIO VIVO
**Para desarrollo y contribuciones.** Es como GitHub pero sin servidores — funciona sobre una red peer-to-peer.

```bash
# Instalar Radicle
curl -sSfL https://radicle.dev/install.sh | sh
# O descargar manual: https://radicle.dev/download

# Clonar el repositorio de scrapers
rad clone rad:z3AqdGcF6fCoGVs64J22zEe85k24A

# Entrar al directorio
cd padim-scrapers

# Listo. Tienes todos los conectores funcionales
python3 vivanuncios_curl.py --colonia "Del Valle" --output datos.json
```

**Ventajas:** Tiene historial Git, actualizable, colaborativo. Mientras haya 2 personas con el repo, existe. ✅ RECOMENDADO.

### Capa 2: Magnet Link (BitTorrent DHT) — DISTRIBUCIÓN MASIVA
**Para descargas rápidas.** Sin servidores, sin trackers, sin dueño.

```
magnet:?xt=urn:sha256:e765112b45b704ee20e6f7afb17458652fe3c455e3cd14b0d50d83171bb018cd&dn=padim-scrapers-v1.0.0.zip&xl=30358
```

1. Instala un cliente torrent (recomendado: [qBittorrent](https://www.qbittorrent.org/))
2. Copia el magnet link de arriba
3. Pégalo en "Añadir enlace torrent"
4. Descarga el ZIP con todos los scrapers

**Ventajas:** No necesita instalación de herramientas raras. BitTorrent es la red más resistente del mundo.

### Capa 3: GitHub (Este Repositorio) — DOCUMENTACIÓN
**Solo README, especificaciones, y disclaimers.** Aquí no hay archivos funcionales, solo las instrucciones para obtenerlos de las Capas 1 y 2.

### ¿Por qué 3 capas?

Para eliminar PADIM-scrapers tendrían que:
1. ❌ Tumbar GitHub → **Posible**, pero solo pierdes la documentación
2. ❌ Tumbar Radicle → **Imposible**, funciona sobre red P2P
3. ❌ Eliminar todos los seeders de BitTorrent → **Imposible**
4. ❌ Censurar todas las menciones → **Imposible**

**El proyecto es indestructible por diseño. Los datos no deberían estar atrapados.**

---

## 🧱 Estructura del Repositorio

```
padim/
├── MANIFIESTO.md       # La visión y el propósito del proyecto
├── CLI/                # Interfaz de línea de comandos
├── connectors/         # Especificaciones y templates para conectores
├── engine/             # Trust Engine + Quality Scoring
├── spec/               # El estándar: schema JSON v1.0
├── tests/              # Tests
└── docs/               # Documentación
```

---

## 📐 El Estándar (v1.0)

El schema PADIM es un formato JSON universal para representar cualquier propiedad inmobiliaria mexicana.

**Funciona con:**
- 🏠 Casas, departamentos, terrenos, locales, oficinas, bodegas, naves industriales
- 💰 Venta, renta, traspaso
- 📍 Cualquier colonia, municipio o estado de México
- 🔗 Múltiples fuentes: portales, APIs, catastro, INEGI, contribución directa

Ver `spec/schema.json` para la especificación completa.

---

## 🧠 Trust Engine — Separa lo real de lo que ya no existe

El 60% de las propiedades en portales mexicanos YA NO ESTÁN DISPONIBLES. PADIM te dice cuáles sí y cuáles no.

| Detector | Detecta | Impacto |
|----------|---------|:-------:|
| 👻 Ghost Listing | Propiedades que ya no existen | -1.0 |
| 💰 Price Anomaly | Precios irrealmente bajos o altos | -1.0 |
| 🚨 Fraude | Keywords fraudulentas + precio anómalo | -0.9 |
| 🎯 Vendor Behavior | Agentes que dejan anuncios viejos | -0.6 |

**Sin servidores. Sin base de datos. Sin suscripciones.** Lógica pura que corre en tu máquina.

---

## 🤝 ¿Cómo contribuir?

| Quiero... | Hago... | Tiempo |
|-----------|---------|:------:|
| Usar los datos | `pip install padim` | 2 min |
| Obtener scrapers | Clonar Radicle o usar magnet link | 2 min |
| Contribuir datos de mi colonia | `padim scrape` desde mi PC | 5 min |
| Construir un conector para mi ciudad | Sigo especificaciones en `connectors/` | 2-3h |
| Mejorar el Trust Engine | Abro un PR en `engine/` | 1h+ |
| Reportar un bug | Abro un issue | 1 min |
| Adoptar el estándar en mi empresa | Integro `spec/schema.json` | 1 día |

---

## 🔗 BACKBONE — Cuando necesitas más que herramientas libres

PADIM te da el poder de los datos. Cuando necesites **escalar**, **BACKBONE** es la capa enterprise:

| PADIM (gratis) | BACKBONE (desde $2,999/mes) |
|----------------|-----------------------------|
| Datos de tu máquina | API 24/7 con SLA 99.9% |
| Trust Engine básico | Trust Scoring completo con ML |
| Sin soporte | Soporte enterprise, onboarding dedicado |
| Sin garantía | AVM certificado con precisión documentada |
| Tú mantienes todo | Webhooks, plugins CRM, integraciones |

**PADIM te da el poder. BACKBONE te da la tranquilidad.**

→ [back-bone.dev](https://back-bone.dev)

---

## 📜 Licencia

- **Estándar (spec/)**: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) — Dominio Público
- **Herramientas (cli/, engine/)**: [MIT](LICENSE)
- **Scrapers funcionales**: Distribuidos bajo Radicle + Magnet Links (ver sección "Scrapers Funcionales")

---

## 🌐 Enlaces

- **Landing**: [padim.enmexico.casa](https://padim.enmexico.casa)
- **Código**: [github.com/PADIM-MX/padim](https://github.com/PADIM-MX/padim)
- **Scrapers (Radicle)**: `rad clone rad:z3AqdGcF6fCoGVs64J22zEe85k24A`
- **Scrapers (Magnet)**: `magnet:?xt=urn:sha256:e765112b45b704ee20e6f7afb17458652fe3c455e3cd14b0d50d83171bb018cd&dn=padim-scrapers-v1.0.0.zip&xl=30358`
- **BACKBONE**: [back-bone.dev](https://back-bone.dev)

---

*"Los datos inmobiliarios de México no deberían estar atrapados. Ahora no lo están."*

**PADIM — Protocolo Abierto de Datos Inmobiliarios de México**
