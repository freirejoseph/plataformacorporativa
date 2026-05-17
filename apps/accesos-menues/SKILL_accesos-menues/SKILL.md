# SKILL_accesos-menues

Portal madre para definir y administrar usuarios, menus, accesos, roles, grupos, portales, modulos, opciones y auditoria.

## Alcance completo
- Crear y mantener usuarios.
- Crear y mantener roles.
- Crear y mantener grupos.
- Crear y mantener portales.
- Crear y mantener modulos.
- Construir menus y submenus.
- Definir opciones finales que abren programas, reportes, URLs o componentes.
- Asignar permisos por usuario, rol y grupo.
- Auditar inicio, fin y duracion de accesos.
- Consultar logs de actividad, errores y seguridad.

## Entradas funcionales
- `usuario`
- `rol`
- `grupo`
- `portal_origen`
- `modulo_origen`

## Regla principal
Este tablero es la fuente de definicion de accesos de toda la plataforma. Si una opcion no pasa por aqui, no debe considerarse parte del sistema corporativo.

## Base tecnica
- Base local principal: SQLite
- Archivo esperado: `portal-data/accesos_menues.sqlite`
- La base vive en la raiz del proyecto para desarrollo local y pruebas en Ubuntu.

## Flujo funcional
```text
Usuario -> Login -> Rol / Grupo / Permisos directos -> Menu permitido -> Opcion final -> Ejecucion -> Log de acceso
```

## Bloques que debe incluir el portal
- Panel de usuarios.
- Panel de roles.
- Panel de grupos.
- Matriz de permisos.
- Constructor de menus.
- Actividad reciente.
- Acciones rapidas.
- Logs de acceso.

## Reglas de seguridad
- La denegacion directa al usuario tiene prioridad.
- Luego aplican permisos directos, por grupo y por rol.
- Todo acceso debe quedar registrado.
- La opcion final debe guardar inicio y cierre de uso.

## Estilo visual
- Tema oscuro corporativo.
- Logo SYSPRO arriba a la izquierda.
- Logo Accesos Digitales arriba a la derecha.
- La UI puede usar datos demo del seed local para mostrar un usuario de referencia, pero el skill no debe fijar personas reales como regla.
- Hoja base: `assets/SKILL_ACCESOSMENUES.css`

## Resultado esperado
Una primera version funcional del portal madre que permita administrar completamente la identidad, la navegacion y los permisos de toda la plataforma.
