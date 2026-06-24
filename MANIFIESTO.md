# 📜 PADIM — Manifiesto del Protocolo Abierto de Datos Inmobiliarios de México

**Versión:** 1.0.0  
**Fecha:** 23 de Junio de 2026  
**Dominio:** PADIM.enmexico.casa  
**Repositorio:** [Por definir — GitHub pending]

---

## I. De la Naturaleza de los Datos

El mercado inmobiliario mexicano padece una fragmentación que no es accidental. Treinta plataformas compiten por el mismo tráfico. Ninguna comparte datos. Los portales mueren con propiedades que ya no existen. Los agentes dejan anuncios viejos para generar llamadas. Los fraudes se multiplican porque no hay manera de verificar.

Este desorden no es un fallo del sistema. **Es el síntoma de un sistema diseñado para la escasez artificial de información.**

En México, los datos de una propiedad —su precio real, su historial, su última transacción— están atrapados en silos que se benefician de mantenerlos cerrados. El resultado es un mercado opaco donde:
- Una startup inmobiliaria gasta 6 a 12 meses reconstruyendo la misma infraestructura de datos
- Un comprador no sabe si el precio que le dan es justo
- Un vendedor no tiene referencia real de mercado
- Un inversionista opera con información que los portales deciden mostrarle

**Esta escasez no es natural. Es una decisión.**

Y como toda decisión, puede revertirse.

---

## II. De la Propuesta

Proponemos la creación del **Protocolo Abierto de Datos Inmobiliarios de México (PADIM)**: un estándar público, gratuito y descentralizado para la representación, intercambio y verificación de datos de propiedades en México.

PADIM no es:
- ❌ Una empresa
- ❌ Un producto
- ❌ Un portal inmobiliario
- ❌ Un servicio de scraping centralizado
- ❌ Propiedad de nadie

PADIM es:
- ✅ Un **estándar** de datos (schema, API spec, trust scoring)
- ✅ Un **conjunto de herramientas** libres (CLI, conectores, validadores)
- ✅ Un **repositorio público** de datos contribuidos por la comunidad
- ✅ Un **protocolo** que cualquier persona, empresa o gobierno puede implementar
- ✅ **De todos y de nadie**

El protocolo opera en tres niveles, como los cimientos, los muros y el techo de una casa común:

### Nivel 1: El Estándar — LO QUE ES
El schema de datos. La especificación REST. El formato de intercambio. Inmutable. Público. Gratis. Cualquier persona puede construir un producto sobre este estándar sin pedir permiso. No requiere mantenimiento. No requiere contribuidores. Existe y existirá.

### Nivel 2: Las Herramientas — LO QUE HACE
El software que permite a cualquiera obtener, validar y compartir datos. Un CLI que se instala con `pip install padim` y desde ese momento cualquier persona puede scrapear su colonia, validar la calidad de los datos, y contribuir al repositorio público. Las herramientas evolucionan. Los conectores se rompen y se reparan. La comunidad los mantiene o los abandona. Pero el estándar sigue intacto.

### Nivel 3: Los Datos — LO QUE CONSTRUYE
El repositorio público de propiedades de México. No es de nadie. Es de quien contribuye. Cada propiedad pasa por un sistema de verificación de calidad antes de ser aceptada. Los datos que no cumplen no aparecen. Los datos que cumplen son de todos.

---

## III. De la Verdad del Mercado

El mercado inmobiliario mexicano tiene un problema de verdades:

**Primera verdad:** La mayoría de las propiedades publicadas en portales YA NO ESTÁN DISPONIBLES. Nadie las da de baja porque tenerlas publicadas genera llamadas. El mercado está lleno de fantasmas.

**Segunda verdad:** No existe una fuente única de verdad. Ni Inmuebles24, ni Vivanuncios, ni Propiedades.com tienen el dataset completo de México. Cada uno tiene una fracción. Ninguno la comparte.

**Tercera verdad:** Los datos del gobierno existen (catastro, SHF, CONAVI, INEGI) pero están dispersos, en formatos distintos, y actualizados con calendarios que no son los del mercado.

**Cuarta verdad:** Quien resuelva este problema de verdades no necesita vender datos. Necesita vender **confianza**.

PADIM no compite con los portales. PADIM es el **lenguaje común** que los portales podrían usar si quisieran interoperar. Y si no quieren, la comunidad puede construir sobre el lenguaje igual.

---

## IV. De la Economía del Protocolo

Un protocolo abierto de datos no es un negocio. Es una **infraestructura pública**. Pero sobre la infraestructura pública se construyen negocios.

La carretera es gratis. Los camiones que la usan pagan peaje en otros lados.

El estándar HTTP es gratis. Las empresas que construyen sobre HTTP valen billones.

OpenStreetMap es gratis. Las empresas que usan OSM para logística valen miles de millones.

**PADIM es gratis. BACKBONE cobra por lo que PADIM no puede dar:**

| PADIM da | BACKBONE cobra |
|----------|----------------|
| Datos crudos | Datos curados con trust scoring |
| API sin SLA | API con SLA 99.9% |
| Trust Engine básico | Trust Engine completo con ML |
| Sin soporte | Soporte enterprise |
| Sin webhooks | Webhooks en tiempo real |
| Sin integraciones | Plugins CRM (Salesforce, GHL, HubSpot) |
| Sin garantía | AVM certificado con precisión documentada |

Este no es un modelo de "versión gratuita vs versión paga". Es un modelo de **infraestructura pública + servicios profesionales**, exactamente como funciona:

- **Red Hat** con Linux (Linux es gratis, Red Hat cobra $10K/año por soporte enterprise)
- **MongoDB** (Community es gratis, Atlas Enterprise cobra)
- **GitLab** (CE es gratis, EE cobra por SSO, auditoría, soporte)

La diferencia es que PADIM no es una empresa. PADIM es un protocolo. No tiene dueño. No se puede comprar, vender ni cerrar. BACKBONE es un servicio comercial que vive sobre el protocolo, igual que cualquier otra empresa que decida construir sobre PADIM.

---

## V. De la Participación

¿Cómo se participa en PADIM?

**1. Usando el estándar** — La especificación está publicada en `padim.enmexico.casa`. Cualquier desarrollador, startup, universidad o dependencia gubernamental puede adoptarla para sus propios fines. No necesita貢獻ir datos. No necesita registrarse. Solo usar el estándar.

**2. Contribuyendo datos** — Con `pip install padim` y un comando como `padim scrape vivanuncios --colonia "Del Valle"`, cualquier persona puede scrapear datos desde su propia computadora. El CLI ejecuta el scraper localmente, valida la calidad con el Trust Engine, y si los datos pasan los filtros, se suben al repositorio público. **Nunca scrapeamos desde un servidor central.** Cada quien scrapea desde su máquina.

**3. Manteniendo conectores** — Los conectores de scraping se rompen cuando los portales cambian. Cada conector tiene un mantenedor. Cualquier desarrollador puede adoptar un conector huérfano. Si un conector se rompe y nadie lo repara en 30 días, se marca como obsoleto.

**4. Validando datos** — El Trust Engine es código abierto. Corre en tu máquina. Cualquier persona puede revisar, criticar y mejorar los detectores de ghost listings, fraudes, anomalías de precio y comportamiento de agentes.

**5. Gobernando el protocolo** — Cuando PADIM crezca, la comunidad elegirá mantenedores. Las decisiones sobre el estándar se tomarán por consenso. Cualquier cambio al schema requiere discusión pública y votación. El protocolo no pertenece a nadie.

---

## VI. De la Relación con BACKBONE

BACKBONE (`https://back-bone.dev`) es la primera API de datos inmobiliarios de México. Es la **implementación de referencia** del protocolo PADIM en su versión enterprise. 

La relación es simbiótica:

**BACKBONE necesita a PADIM** porque BACKBONE, como empresa, no puede scrapear todo México. BACKBONE gasta recursos limitados en curaduría, ML, infraestructura y soporte. PADIM, como comunidad, puede cubrir colonias y zonas que BACKBONE nunca alcanzaría.

**PADIM necesita a BACKBONE** porque BACKBONE produce datos curados de alta calidad que retroalimentan el dataset público. BACKBONE entrena modelos de ML que mejoran el Trust Engine. BACKBONE paga por infraestructura que beneficia a todo el ecosistema.

**La línea es clara:**
- PADIM = los datos abiertos, el estándar, las herramientas libres
- BACKBONE = el servicio enterprise, la curaduría, el SLA, el soporte

Uno no puede cerrar al otro. Si BACKBONE desapareciera mañana, PADIM seguiría existiendo. Si PADIM desapareciera, BACKBONE perdería su fuente de datos comunitaria pero conservaría su propio pipeline.

Esta separación es la garantía de que el protocolo nunca será secuestrado por intereses comerciales.

---

## VII. Del Llamado

A desarrolladores mexicanos que han reconstruido la misma infraestructura de datos tres veces en su carrera: **esto es para ustedes.**

A startups proptech que gastan 6 meses en scraping antes de escribir una sola línea de su producto: **esto es para ustedes.**

A académicos e investigadores que necesitan datos del mercado inmobiliario mexicano para sus tesis, papers y políticas públicas: **esto es para ustedes.**

A agentes y brokers que saben que el mercado está roto y quieren cambiarlo desde adentro: **esto es para ustedes.**

A ciudadanos que quieren saber cuánto vale realmente su casa: **esto es para ustedes.**

El mercado inmobiliario mexicano no será liberado por una empresa, un gobierno o un salvador. Será liberado por **un protocolo** que cualquiera puede usar, cualquiera puede mejorar y nadie puede cerrar.

PADIM no pide permiso. PADIM publica el estándar. Construye las herramientas. Y deja que la comunidad haga el resto.

---

**No esperes a que alguien más lo haga.**  
**El protocolo está aquí. Las herramientas están aquí.**  
**La única pregunta es: ¿vas a contribuir o vas a esperar?**

— PADIM, 23 de Junio de 2026  
`PADIM.enmexico.casa`
