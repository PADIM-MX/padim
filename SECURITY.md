# Política de Seguridad

## Reportar una Vulnerabilidad

Si encuentras una vulnerabilidad de seguridad en PADIM, **por favor no abras 
un Issue público**. En su lugar:

1. Envía un correo a **seguridad@back-bone.dev**
2. Incluye:
   - Descripción del problema
   - Pasos para reproducirlo
   - Impacto potencial
   - Sugerencia de solución (opcional)

### Tiempo de respuesta
- Acusamos recibo en < 48 horas
- Investigamos y respondemos con plan de acción en < 7 días
- Publicamos un advisory después de aplicar la corrección

## Buenas Prácticas

- No ejecutes scrapers sin rate limiting (respetar `robots.txt`)
- No almacenes datos personales (nombres, teléfonos, correos) en el dataset
- Reporta conectores rotos que puedan exponer datos no públicos
- Usa el Trust Engine para validar datos antes de integrarlos