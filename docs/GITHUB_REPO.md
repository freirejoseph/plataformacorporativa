# GitHub del Proyecto

Repositorio remoto:
- `https://github.com/freirejoseph/plataformacorporativa.git`

## Que debe vivir aqui
Este repositorio debe concentrar:
- la documentacion del Portal Corporativo
- el subportal `accesos-menues`
- los skills en `docs/`
- los contratos visuales en `docs/`
- el codigo fuente en `apps/`, `core/`, `shared/` e `infra/`

## Convencion del proyecto
- El nombre logico de la experiencia de usuario es `Portal Corporativo`.
- El nombre de la raiz madre del desarrollo es `plataformacorporativa`.
- La verdad funcional se mantiene sincronizada entre local y Ubuntu.
- Todo cambio importante debe dejar referencia en `RevisionesQA/`.

## Reglas de colaboracion
- No duplicar skills por portal.
- No dejar reglas dispersas en carpetas sueltas.
- No tocar el portal ya publicado en el servidor sin definir puerto o ruta aislada.
- Mantener siempre documentado el flujo de entrada, permisos y navegacion.

## Estado actual
- `docs/` ya centraliza los `SKILL`.
- `accesos-menues` es el primer subportal funcional.
- El Portal Corporativo es el punto de entrada logico para los usuarios.

## Como probar la vista corporativa
- abrir `apps/portal-corporativo/index.html`
- o servir `apps/portal-corporativo/` con `python -m http.server 5173`
- la pagina de prueba muestra el shell visual del Portal Corporativo y el acceso al subportal `Usuarios y Accesos`

## Sincronizacion automatica
- `infra/scripts/sync_and_publish.py`
- `infra/scripts/sync_and_publish.ps1`
- modo watch recomendado para cambios frecuentes: `--watch --interval 60 --push`
