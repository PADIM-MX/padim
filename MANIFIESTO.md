# 📜 PADIM — Manifiesto del Protocolo Abierto de Datos Inmobiliarios de México

**Versión:** 2.0.1  
**Fecha:** 2 de Julio de 2026  
**Dominio:** PADIM.enmexico.casa  
**Repositorio:** https://github.com/PADIM-MX/padim

---

## I. De la Naturaleza de los Datos

El mercado inmobiliario mexicano está compuesto por treinta plataformas compitiendo por la misma audiencia. Cada una opera su propio conjunto de datos. Ninguna comparte información con las otras.

Esta fragmentación no es el resultado de una conspiración ni de mala fe. Es la consecuencia predecible de un ecosistema donde cada participante —portal, agente, desarrollador— toma decisiones racionales para su propio contexto. El problema es que esas decisiones individuales, sumadas, producen un resultado que nadie buscó: un mercado donde la información está atrapada en silos que no se comunican entre sí.

Las consecuencias son medibles:

- Una startup inmobiliaria gasta de 6 a 12 meses reconstruyendo la misma infraestructura de datos que otra startup ya construyó al otro lado de la ciudad.
- Un comprador no puede verificar si el precio que le ofrecen corresponde al valor real del mercado.
- Un vendedor no tiene una referencia confiable para poner su propiedad.
- Un inversionista opera con la fracción de información que los portales deciden mostrarle.

Ninguno de estos actores creó este problema. Todos lo heredaron. Pero todos pueden participar en la solución.

**Esta fragmentación no es una ley natural. Es una circunstancia que podemos cambiar juntos.**

---

## II. De la Propuesta

Proponemos la creación del **Protocolo Abierto de Datos Inmobiliarios de México (PADIM)**: un estándar público, gratuito y descentralizado para la representación, intercambio y verificación de datos de propiedades en México.

**PADIM no es:**
- Una empresa
- Un producto
- Un portal inmobiliario
- Un servicio de scraping centralizado
- Propiedad de nadie

**PADIM es:**
- Un **estándar** de datos (schema, API spec, trust scoring)
- Un **conjunto de herramientas** libres (CLI, conectores, validadores)
- Un **repositorio público** de datos contribuidos por la comunidad
- Un **protocolo** que cualquier persona, empresa o gobierno puede implementar
- **De todos y de nadie**

PADIM existe para servir a todos los actores del ecosistema: portales que quieran interoperar, agentes que busquen transparencia, startups que necesiten datos confiables, y ciudadanos que merecen saber el valor real de su patrimonio.

El protocolo opera en tres niveles:

### Nivel 1: El Estándar — LO QUE ES
El schema de datos. La especificación REST. El formato de intercambio. Inmutable. Público. Gratis. Cualquier persona puede construir un producto sobre este estándar sin pedir permiso. No requiere mantenimiento. No requiere contribuidores. Existe y existirá.

### Nivel 2: Las Herramientas — LO QUE HACE
El software que permite a cualquiera obtener, validar y compartir datos. Un CLI que se instala con `pip install padim` y desde ese momento cualquier persona puede extraer información de su colonia, validar la calidad de los datos, y contribuir al repositorio público. Las herramientas evolucionan. Los conectores se rompen y se reparan. La comunidad los mantiene o los abandona. Pero el estándar sigue intacto.

### Nivel 3: Los Datos — LO QUE CONSTRUYE
El repositorio público de propiedades de México. No es de nadie. Es de quien contribuye. Cada propiedad pasa por un sistema de verificación de calidad antes de ser aceptada. Los datos que no cumplen no aparecen. Los datos que cumplen son de todos.

---

## III. De la Realidad del Mercado

El mercado inmobiliario mexicano no es un mercado. Son treinta mercados paralelos que no se hablan entre sí.

Este no es un problema menor de coordinación. Es la razón estructural por la que el mercado opera con la mitad de su capacidad potencial. Para entenderlo, hay que mirar el problema desde su causa raíz, no desde sus síntomas visibles.

### Primera verdad: México no tiene un mercado inmobiliario unificado. Tiene fragmentos que no conectan.

Hoy, los datos de una propiedad —su precio real, su historial de transacciones, su situación legal— están dispersos en al menos diez lugares distintos: el portal donde se publicó, el catastro municipal, el Registro Público de la Propiedad, el buró de crédito, la SHF, el sistema del notario, el CRM del agente, la plataforma del valuador, el sistema del banco, y la memoria del vendedor. Ninguno de estos sistemas se comunica con los otros.

El resultado es que cada participante opera con una fracción de la información disponible. Un comprador compara precios en tres portales y cree tener una visión completa, cuando en realidad está viendo el mismo 15% del mercado repetido tres veces. Un desarrollador fija precios basándose en los datos de su zona, sin saber que al otro lado de la ciudad hay un proyecto similar vendiendo 20% más barato. Un banco evalúa una hipoteca sin poder verificar de forma confiable el historial de la propiedad.

Esta fragmentación no es culpa de nadie en particular. Los portales construyeron sus bases de datos porque era lo que necesitaban para operar. Los gobiernos estatales tienen sus propios sistemas porque cada entidad es autónoma. Los agentes guardan su información en sus CRM porque no hay un estándar para compartirla. Cada decisión fue racional en su contexto. Pero juntas producen un sistema que nadie diseñó y que perjudica a todos.

**Lo que esto significa en la práctica:**
- Una startup inmobiliaria gasta de 6 a 12 meses reconstruyendo la misma infraestructura de datos que otra startup ya construyó.
- Un comprador visita 10 propiedades antes de encontrar una que realmente existe al precio publicado.
- Un vendedor acepta la primera oferta seria porque no tiene forma de saber si es justa.
- Un inversionista internacional decide no entrar al mercado mexicano porque no hay datos confiables.

**PADIM resuelve esto:** No creando datos nuevos, sino creando un lenguaje común para que los datos que ya existen puedan fluir entre quienes los necesitan. No es un portal más. Es el estándar que permite que cualquier portal, agencia o institución publique y consuma datos en un formato que todos entiendan.

### Segunda verdad: El costo de la desinformación lo pagan todos, pero nadie lo mide.

Cuando un comprador pierde un mes visitando ghost listings, el costo no aparece en ninguna estadística. Cuando un agente paga ocho mil pesos por un lead que resulta ser un número equivocado, ese dinero no se reporta como pérdida del mercado. Cuando un banco rechaza una hipoteca porque no puede verificar el valor de una propiedad, esa transacción simplemente no ocurre.

Pero estos costos existen y son enormes:

| Dónde se pierde valor | Cuánto | Quién lo paga |
|---|---|---|
| Spread entre precio ofertado y precio real de venta | 8% a 15% del valor de cada transacción | Compradores y vendedores |
| Costo de intermediación en portales | $8,000 a $15,000 millones de pesos al año | Agentes (lo trasladan a compradores) |
| Tiempo perdido del comprador en ghost listings | 3 a 6 semanas por búsqueda | 45% de compradores reportan problemas |
| Litigios por información incorrecta o fraudes | ~50,000 casos al año en tribunales civiles | Compradores y el sistema judicial |
| Originación hipotecaria inflada por falta de datos | $15,000 a $25,000 por crédito | Compradores con crédito |

En conjunto, se estima que la falta de un estándar de datos le cuesta al mercado inmobiliario mexicano entre 500 mil millones y un billón de pesos al año en ineficiencias, costos evitables y transacciones que no ocurren.

**PADIM resuelve esto:** Reduciendo el ghost listings de 30-50% a menos de 5%, bajando el costo de adquisición de leads de $200-800 a $50-200 pesos, y permitiendo que el costo de originación hipotecaria se reduzca a la mitad al tener datos verificables desde el origen.

### Tercera verdad: El mercado hipotecario mexicano podría ser tres veces más grande.

México tiene una penetración hipotecaria de aproximadamente 12% del PIB. Estados Unidos tiene 50%. Chile tiene 40%. Esto no es porque los mexicanos no quieran comprar casa: es porque el sistema no tiene la información necesaria para prestar de manera eficiente.

Los bancos no pueden verificar el valor real de las propiedades de forma confiable. Los avalúos se hacen caso por caso y cuestan miles de pesos. El historial de una propiedad —si ha tenido gravámenes, si su precio ha sido consistente— no está disponible en ningún sistema al que el banco pueda consultar automáticamente.

De cada cien propiedades que se venden, solo veinticinco o treinta se financian con crédito hipotecario. El resto son compras de contado, que excluyen a la mayoría de la población. Si la penetración hipotecaria mexicana estuviera al nivel de Chile, el mercado de crédito sería de aproximadamente 5.4 billones de pesos, tres veces su tamaño actual.

**PADIM resuelve esto:** Proporcionando un historial verificable de cada propiedad —precios de transacciones anteriores, avalúos registrados, situación legal— que los bancos pueden consultar a través de una API estándar. Esto reduce el riesgo de originación y permite que más crédito fluya al sector.

### Cuarta verdad: Cada actor del ecosistema cumple una función necesaria. Lo que falta es la infraestructura para que funcionen mejor.

Los portales inmobiliarios han construido la audiencia que hoy existe. Invierten millones en tráfico, tecnología y experiencia de usuario. Sin ellos, el mercado digital inmobiliario en México no existiría.

Los agentes y brokers son el canal de ventas más importante del país. Conocen las colonias, las dinámicas locales, los precios reales. Resuelven problemas que ningún algoritmo puede resolver todavía.

Los desarrolladores construyen las propiedades que el país necesita. Arriesgan capital, navegan regulaciones, generan empleo.

El gobierno, a través del catastro, la SHF, el INFONAVIT y el Registro Público, produce la información oficial que da certeza jurídica a las transacciones.

Ninguno de estos actores está haciendo algo mal. Todos están haciendo lo que deben hacer dentro del sistema que heredaron. El problema no son ellos. El problema es que no hay un lenguaje común entre ellos.

**PADIM no reemplaza a nadie. PADIM conecta a todos.**

Un portal que adopte PADIM puede ofrecer a sus usuarios datos verificados de otras fuentes, sin perder su identidad ni su audiencia. Un agente que use PADIM puede demostrar con datos su reputación y la calidad de sus listados. Un banco que integre PADIM puede reducir su costo de originación y prestar más. Un gobierno que publique datos en PADIM puede mejorar la recaudación y la planeación urbana.

PADIM es el protocolo que permite que todos estos actores —cada uno con su función, sus incentivos y su valor— puedan coordinarse sin perder su autonomía.

---

## IV. De la Economía del Protocolo

Un protocolo abierto de datos no es un negocio. Es una infraestructura pública. Pero sobre la infraestructura pública se construyen negocios.

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

Este no es un modelo de "versión gratuita vs versión paga". Es un modelo probado de **infraestructura pública + servicios profesionales**, exactamente como funciona con Linux y Red Hat, o con MongoDB Community y Atlas.

La diferencia fundamental es que PADIM no es una empresa. PADIM es un protocolo. No tiene dueño. No se puede comprar, vender ni cerrar. BACKBONE es un servicio comercial que existe sobre el protocolo, exactamente como cualquier otra empresa que decida construir sobre PADIM.

---

## V. De la Participación

PADIM se construye con la participación de quienes decidan sumarse. No hay una membresía, ni una cuota, ni un permiso que pedir.

**1. Usando el estándar** — La especificación está publicada en `padim.enmexico.casa`. Cualquier desarrollador, startup, universidad o dependencia gubernamental puede adoptarla para sus propios fines. No necesita contribuir datos. No necesita registrarse. Solo usar el estándar.

**2. Contribuyendo datos** — Con `pip install padim` y un comando como `padim scrape --colonia "Del Valle"`, cualquier persona puede extraer datos desde su propia computadora. El CLI ejecuta la extracción localmente, valida la calidad con el Trust Engine, y si los datos pasan los filtros, se integran al repositorio público. Nunca extraemos desde un servidor central. Cada quien contribuye desde su máquina.

**3. Manteniendo conectores** — Los conectores se actualizan cuando los portales cambian. Cada conector tiene un mantenedor. Cualquier desarrollador puede adoptar un conector huérfano. Si un conector se rompe y nadie lo repara en 30 días, se marca como obsoleto.

**4. Validando datos** — El Trust Engine es código abierto. Corre en tu máquina. Cualquier persona puede revisar, criticar y mejorar los detectores de propiedades no disponibles, anomalías de precio y calidad de información.

**5. Gobernando el protocolo** — Cuando PADIM crezca, la comunidad elegirá mantenedores. Las decisiones sobre el estándar se tomarán por consenso. Cualquier cambio al schema requiere discusión pública y votación. El protocolo no pertenece a nadie.

---

## VI. De la Relación con BACKBONE

BACKBONE (`https://back-bone.dev`) es la primera API de datos inmobiliarios de México. Es una **implementación del estándar PADIM** en su versión enterprise.

La relación es complementaria:

**BACKBONE necesita a PADIM** porque BACKBONE, como empresa, no puede cubrir todo México. BACKBONE concentra sus recursos en curaduría, infraestructura y soporte. PADIM, como comunidad, puede alcanzar colonias y zonas que BACKBONE nunca cubriría por sí solo.

**PADIM necesita a BACKBONE** porque BACKBONE produce datos curados de alta calidad que retroalimentan el acervo público. BACKBONE entrena modelos que mejoran el Trust Engine. BACKBONE financia infraestructura que beneficia a todo el ecosistema.

**La línea es clara:**
- PADIM = los datos abiertos, el estándar, las herramientas libres
- BACKBONE = el servicio enterprise, la curaduría, el SLA, el soporte

Uno no puede cerrar al otro. Si BACKBONE desapareciera mañana, PADIM seguiría existiendo. Si PADIM desapareciera, BACKBONE perdería su fuente de datos comunitaria pero conservaría su propio pipeline.

Esta separación es la garantía de que el protocolo nunca será secuestrado por intereses comerciales.

---

## VII. Del Llamado

A desarrolladores mexicanos que han reconstruido la misma infraestructura de datos tres veces en su carrera: **esto es para ustedes.**

A startups proptech que gastan los primeros meses de su existencia en scraping antes de escribir una sola línea de su producto: **esto es para ustedes.**

A académicos e investigadores que necesitan datos del mercado inmobiliario mexicano para sus tesis, papers y políticas públicas: **esto es para ustedes.**

A agentes y brokers que ven todos los días lo que funciona y lo que no en el mercado real: **esto es para ustedes.**

A ciudadanos que quieren saber cuánto vale realmente su casa: **esto es para ustedes.**

El mercado inmobiliario mexicano no será transformado por una empresa, un gobierno o un líder individual. Será transformado por **un protocolo** que cualquiera puede usar, cualquiera puede mejorar y nadie puede cerrar.

PADIM no pide permiso. PADIM publica el estándar. Construye las herramientas. Y confía en que la comunidad hará el resto.

---

**El protocolo está aquí. Las herramientas están aquí.**  
**La única pregunta es si decides sumarte.**

— PADIM, 2 de Julio de 2026  
`PADIM.enmexico.casa`
