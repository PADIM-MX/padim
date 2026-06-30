# PADIM — Estructura Legal y Gobierno

## Situación Actual (v2.0.0)

PADIM opera actualmente sin personería jurídica. El repositorio está bajo la
organización `PADIM-MX` en GitHub. Los contribuidores individuales son
responsables de sus propias contribuciones.

## Riesgo Legal Identificado

Los scrapers funcionales (en repositorio separado) podrían:
- Violar términos de servicio de portales inmobiliarios
- Recibir cartas de cese y desistimiento (C&D)
- Ser blanco de acciones legales

**Mientras PADIM no tenga personalidad jurídica, esos riesgos recaen en
contribuidores individuales.**

## Solución Propuesta: PADIM A.C.

### ¿Qué es una A.C.?

Una **Asociación Civil (A.C.)** en México es una figura legal que permite:
- Tener personalidad jurídica propia
- Recibir donaciones deducibles de impuestos (con RFC donataria autorizada)
- Firmar convenios con gobiernos (SHF, Catastro, CONAVI)
- Separar la responsabilidad legal de los miembros

### Costos y Proceso

| Concepto | Costo estimado | Tiempo |
|----------|---------------|--------|
| Constitución ante notario | $3,000 - $5,000 MXN | 1 semana |
| RFC ante SAT | $0 | 3-5 días hábiles |
| Donataria autorizada (opcional) | $0 | 3-6 meses |
| Registro ante INDESOL | $0 | 1-2 semanas |
| **Total** | **~$5,000 MXN** | **~3 semanas** |

### Estatutos Propuestos

La A.C. tendría:

1. **Objeto social:** Promover datos abiertos inmobiliarios en México mediante
   estándares, herramientas y repositorios públicos.
2. **Órganos:**
   - Asamblea General (todos los contribuidores activos)
   - Consejo Directivo (3-5 mantenedores elegidos)
   - Comité Técnico (revisiones del schema y protocolo)
3. **Propiedad intelectual:**
   - PADIM (marca, dominio, estándar) pertenece a la A.C.
   - BACKBONE (marca, producto) puede usar PADIM bajo licencia
   - Ningún miembro puede apropiarse del protocolo

### Escudo Legal Temporal (mientras se constituye la A.C.)

```
┌─────────────────────────────────────────────────┐
│              ESTRUCTURA DE AISLAMIENTO           │
├─────────────────────────────────────────────────┤
│                                                  │
│  GitHub: PADIM-MX/padim                          │
│  └── Solo documentación, schema, CLI, engine     │
│  └── NO contiene scrapers funcionales            │
│  └── Disclaimer legal en README                  │
│                                                  │
│  Repositorio SEPARADO: PADIM-MX/padim-scrapers   │
│  └── Contiene los conectores funcionales         │
│  └── LICENSE propio con disclaimer               │
│  └── README advierte sobre ToS de portales       │
│                                                  │
│  CLI (pip install padim)                         │
│  └── Descarga scrapers desde el repo separado    │
│  └── Advertencia legal al primer scrape          │
│                                                  │
│  Radicle / IPFS / Magnet                         │
│  └── Canales descentralizados                    │
│  └── Sin control central posible                 │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Disclaimer Legal (ya actualizado en README)

```
⚠️ AVISO LEGAL

PADIM es un proyecto de código abierto que proporciona ESPECIFICACIONES
y HERRAMIENTAS para acceder a datos inmobiliarios públicos.

AL USAR ESTE PROYECTO, ACEPTAS QUE:
- Eres el único responsable del cumplimiento legal en tu jurisdicción
- Los conectores funcionales se distribuyen por canales separados
- Este proyecto no almacena, procesa ni distribuye datos personales
- Los datos obtenidos deben usarse de acuerdo con los ToS de cada fuente
- PADIM A.C. no se hace responsable del uso que terceros den al software
```

## Timeline Propuesto

| Fecha | Hito |
|-------|------|
| Julio 2026 | Publicar plan de constitución en GitHub Discussions |
| Agosto 2026 | Reunión virtual de contribuidores para aprobar estatutos |
| Septiembre 2026 | Constitución ante notario |
| Octubre 2026 | RFC + registro fiscal |
| Noviembre 2026 | Solicitud de donataria autorizada |
| Diciembre 2026 | Primera asamblea general |
