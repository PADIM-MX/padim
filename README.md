# 🏠 PADIM — Protocolo Abierto de Datos Inmobiliarios de México

**Versión 2.0.0** — Deja de perder 6 meses construyendo la misma infraestructura que todos los demás. Empieza a construir productos que tus clientes realmente necesitan.

---

## ⚡ En 5 minutos tienes datos de cualquier colonia

```bash
pip install padim

# Datos de una colonia en segundos
padim scrape vivanuncios --colony "Del Valle" --output delvalle.json

# Valida que los datos sean correctos
padim validate delvalle.json

# Calcula qué tan confiables son
padim quality delvalle.json

# Lista fuentes disponibles
padim sources

# Sirve tu propia API REST local
padim serve --port 8080
# → http://localhost:8080/docs  (documentación interactiva)
# → http://localhost:8080/v1/stats  (estadísticas)
# → http://localhost:8080/v1/market/Del%20Valle  (análisis de colonia)
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

Los conectores funcionales para scraping NO están en este repositorio principal. Se distribuyen a través de **4 canales independientes** sincronizados automáticamente por CI/CD. Todos son respaldos del mismo código, para que el proyecto sea **indestructible por diseño**.

### Capa 1: GitHub (Primario) — CÓDIGO + COLABORACIÓN
**Interfaz humana principal.** Pull requests, issues, discusiones, y el código fuente vivo.

```bash
git clone https://github.com/PADIM-MX/padim-scrapers
cd padim-scrapers
python3 vivanuncios_curl.py --colony "Del Valle" --output datos.json
```

**Ventajas:** Todo developer mexicano sabe usar GitHub. PRs, reviews, CI. ✅ RECOMENDADO para contribuir.

### Capa 2: Radicle (Red P2P) — RESPALDO DESCENTRALIZADO
**Espejo automático del repositorio.** Cada push a GitHub se refleja en Radicle mediante CI. No requiere intervención humana.

```bash
rad clone rad:z3AqdGcF6fCoGVs64J22zEe85k24A
cd padim-scrapers
```

**Ventajas:** Historial Git completo, actualizable, colaborativo. Mientras haya 2 personas con el repo, existe. **Se sincroniza SOLO** via GitHub Actions. ✅ RESPALDO AUTOMÁTICO.

### Capa 3: IPFS (Contenido) — DISTRIBUCIÓN INMUTABLE
**Cada release se publica automáticamente a IPFS.** El CID (Content ID) es la prueba criptográfica de que el contenido no ha sido alterado.

```
# El CI genera automáticamente:
# 1. ZIP del release
# 2. CID de IPFS
# 3. Pin en 3+ nodos gratuitos (Pinata, Filebase)
```

**Ventajas:** Contenido inmutable, IPFS es la red más resistente del mundo. ✅ AUTOMATIZADO.

### Capa 4: Magnet Link (BitTorrent DHT) — GENERADO AUTOMÁTICAMENTE
**Cada release genera su propio magnet link.** El CI calcula el SHA256, crea el torrent, y lo sube a GitHub Releases.

```
magnet:?xt=urn:sha256:[AUTOMATIC]&dn=padim-scrapers-v2.0.0.zip
```

**Ventajas:** No necesita instalación de herramientas raras. **Se regenera solo en cada release.** Ya no es estático. ✅ AUTOMATIZADO.

### ¿Por qué 4 capas y cómo se sincronizan?

```
[Dev hace PR en GitHub] → [CI tests] → [Merge a main]
    ↓                        ↓               ↓
  Radicle mirror          IPFS pin        ZIP + Magnet
  (automático)            (automático)    (GitHub Release)
```

Para eliminar PADIM-scrapers tendrían que:
1. ❌ Tumbar GitHub → **Posible**, pero Capas 2, 3, 4 siguen funcionando
2. ❌ Tumbar Radicle → **No pueden**, red P2P
3. ❌ Censurar IPFS → **No pueden**, los CIDs están everywhere
4. ❌ Eliminar todos los seeders de BitTorrent → **No pueden**
5. ❌ Censurar todas las menciones → **No pueden**

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

| Componente | Licencia | Archivo |
|-----------|----------|---------|
| **Estándar (spec/)** | [CC0 1.0](spec/LICENSE) — Dominio público | [spec/LICENSE](spec/LICENSE) |
| **Trust Engine (engine/)** | [AGPL v3](engine/LICENSE) — Copyleft fuerte | [engine/LICENSE](engine/LICENSE) |
| **CLI (cli/)** | [MIT](cli/LICENSE) — Permisiva | [cli/LICENSE](cli/LICENSE) |
| **Datos** | [ODbL v1.0](LICENSE-ODbL.md) — Atribución + Share-Alike | [LICENSE-ODbL.md](LICENSE-ODbL.md) |
| **Raíz del proyecto** | Explicación de sub-licencias | [LICENSE](LICENSE) |

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
