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

Los conectores funcionales para scraping se distribuyen desde un repositorio público independiente:

```bash
git clone https://github.com/Trogloautoegocrata/mx-property-scrapers
cd mx-property-scrapers
```

**Licencia:** BSL 1.1 — uso no comercial libre.

---

## 📜 Licencia

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
| Obtener scrapers | `git clone https://github.com/Trogloautoegocrata/mx-property-scrapers` | 2 min |
| Contribuir datos de mi colonia | `padim scrape` desde mi PC | 5 min |
| Construir un conector para mi ciudad | Sigo especificaciones en `connectors/` | 2-3h |
| Mejorar el Trust Engine | Abro un PR en `engine/` | 1h+ |
| Reportar un bug | Abro un issue | 1 min |
| Adoptar el estándar en mi empresa | Integro `spec/schema.json` | 1 día |

---

## 📖 PADIM es un proyecto independiente

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
- **Scrapers**: [mx-property-scrapers](https://github.com/Trogloautoegocrata/mx-property-scrapers)

---

*"Los datos inmobiliarios de México no deberían estar atrapados. Ahora no lo están."*

**PADIM — Protocolo Abierto de Datos Inmobiliarios de México**
