# SKILL_Plataforma

Reglas globales de la plataforma corporativa, comunes a todos los tableros.

## Proposito
Definir el contrato base que deben seguir todos los agentes, tableros y modulos de la plataforma.

## Estructura raiz
- `apps/`: tableros madre y tableros departamentales.
- `core/`: contexto global, sesion, permisos y auditoria.
- `shared/`: piezas reutilizables compartidas.
- `infra/`: despliegue, scripts, nginx, docker y respaldo.
- `docs/`: arquitectura, flujos, permisos y onboarding.
- `RevisionesQA/`: reportes de revision de cada agente.

## Convenciones
- Usar nombres claros y consistentes para archivos, carpetas, tablas y endpoints.
- Mantener una unica fuente de verdad por dominio.
- Evitar duplicar logica entre `apps/`, `core/` y `shared/`.
- Preferir ASCII en archivos nuevos salvo que el archivo ya tenga tildes o formato especifico.

## Seguridad
- No versionar secretos.
- `.env` es solo para desarrollo local o remoto controlado.
- Toda entrada de usuario debe validarse antes de persistirla.
- Toda salida HTML debe evitar XSS.
- Toda accion sensible debe quedar auditada.

## API
- Los endpoints deben responder JSON consistente.
- Los cambios de estado deben usar metodos HTTP correctos.
- Las respuestas de error deben ser claras y no exponer secretos.
- Los modulos deben respetar el contrato comun de entrada: `usuario`, `rol`, `grupo`, `portal_origen`, `modulo_origen`.

## Base de datos
- SQLite se usa para desarrollo local y pruebas.
- Los esquemas deben vivir documentados y versionados.
- Toda tabla importante debe tener claves, indices y relaciones claras.

## Frontend
- El estilo corporativo debe ser consistente entre tableros.
- Reutilizar componentes comunes en vez de copiar bloques de HTML.
- Usar accesibilidad basica: labels, roles, contraste y navegacion por teclado.

## Testing
- Toda mejora funcional debe considerar al menos una prueba.
- Los cambios de API deben tener pruebas de humo o integracion.

## Desarrollo
- Leer el `SKILL.md` del tablero antes de editar.
- Si un tablero ya tiene skill especifico, seguir ese skill antes que reglas genericas.
- Si falta definicion de negocio, documentarla antes de codificar.
- Al terminar cualquier cambio, sincronizar siempre la copia local y la copia de Ubuntu.
- La sincronizacion final es obligatoria antes de cerrar una tarea.

## Prioridad de la plataforma
1. `accesos-menues`
2. `portal-corporativo`
3. `administracion-general`
4. Los tableros de negocio
