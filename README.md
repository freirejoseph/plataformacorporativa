# plataformacorporativa

Repositorio madre de la plataforma corporativa para el ecosistema de portales y tableros.

## Proposito
Esta base organiza el desarrollo de:
- `Plataforma Corporativa`: punto de entrada visual para usuarios.
- `accesos-menues`: subportal madre de administracion de usuarios, roles, grupos, menus y permisos.
- futuros tableros de negocio: compras, inventario, produccion, finanzas, CxC, CxP, reportes, RRHH y otros.

## Estructura principal
- `apps/`: subportales y modulos funcionales.
- `core/`: base transversal de sesion, auditoria, gateway y contexto de usuario.
- `shared/`: utilidades comunes, permisos, auth, menu router y componentes compartidos.
- `docs/`: fuente unica de verdad para skills, contratos visuales y referencias tecnicas.
- `infra/`: despliegue, scripts, nginx, systemd, docker y utilidades operativas.
- `portal-data/`: datos locales, SQLite y soportes de desarrollo.
- `RevisionesQA/`: observaciones y pendientes de revision.

## Fuentes de verdad
Todos los `SKILL` del proyecto viven en `docs/`:
- [Indice de skills](docs/SKILLS_INDEX.md)
- [Plataforma Corporativa](docs/SKILLPortalCorporativo.md)
- [Plataforma Corporativa CSS](docs/SKILLPortalCorporativo.css)
- [accesos-menues](docs/SKILL_accesos-menues.md)
- [accesos-menues CSS](docs/SKILL_accesos-menues.css)
- [Stack tecnico](docs/stack-tecnico.md)

## Raiz de trabajo
La carpeta madre del desarrollo es:
- `/home/plataformacorporativa` en Ubuntu

La copia local se usa como respaldo y espejo de trabajo.

## Flujo de desarrollo
1. Se edita en local o por SSH remoto.
2. Se valida la funcionalidad en Ubuntu.
3. Al final de cada cambio se sincroniza local y Ubuntu.
4. Se documenta cualquier hallazgo en `RevisionesQA/`.

## Sincronizacion automatica
Use el script de automatizacion para mantener el espejo y publicar cambios:

```powershell
python .\infra\scripts\sync_and_publish.py --watch --interval 60 --push
```

La version PowerShell esta en:
- `infra/scripts/sync_and_publish.ps1`

## Probar la Plataforma Corporativa
La vista inicial del portal se puede probar abriendo:
- `apps/portal-corporativo/index.html`

O levantando un servidor estatico en el folder:

```powershell
cd apps\portal-corporativo
python -m http.server 5173
```

Luego abre:
- `http://127.0.0.1:5173/`

## Publicacion
El portal actual del servidor Ubuntu ya existe y no debe tocarse sin validacion.
El nuevo desarrollo se maneja como portal aislado y su publicacion debe hacerse en el puerto o ruta que corresponda al subportal correspondiente.

## Arranque rapido
Para el subportal `accesos-menues`:
- revisar `apps/accesos-menues/backend/main.py`
- revisar `docs/SKILL_accesos-menues.md`
- revisar `docs/SKILLPortalCorporativo.md`
- revisar `docs/SKILLS_INDEX.md`

## Repositorio GitHub
Repositorio remoto asociado:
- `https://github.com/freirejoseph/plataformacorporativa.git`
