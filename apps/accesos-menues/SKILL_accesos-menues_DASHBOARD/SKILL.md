# SKILL_accesos-menues_DASHBOARD

Dashboard madre para resumir usuarios, roles, grupos, menus, permisos, portales y actividad del sistema.

## Proposito
Definir la configuracion del dashboard principal del portal de accesos y menus, con tarjetas, tablas, graficas, calculos y fuentes de datos.

## Alcance
Este dashboard resume:
- Usuarios activos.
- Roles creados.
- Grupos.
- Menus configurados.
- Portales y modulos.
- Accesos de hoy.
- Sesiones en linea.
- Actividad reciente.
- Matriz de permisos.

## Reglas de datos
- La informacion base debe salir de SQLite local.
- Las tablas y vistas deben vivir en el area compartida.
- Todo indicador debe declarar su tabla origen.
- Los filtros por usuario y rol son obligatorios.
- Ningun KPI debe mostrar datos fuera del alcance del usuario.

## Fuentes tecnicas esperadas
- `usuarios`
- `roles`
- `grupos`
- `portales`
- `modulos`
- `menus`
- `opciones_programa`
- `permisos_rol`
- `permisos_usuario`
- `permisos_grupo`
- `log_accesos`
- `log_actividad`
- `sesiones`

## Componentes visuales
- KPI de usuarios activos.
- KPI de roles creados.
- KPI de menus configurados.
- KPI de accesos hoy.
- KPI de accesos en linea.
- Matriz de permisos.
- Lista de usuarios.
- Lista de roles.
- Actividad reciente.
- Acciones rapidas.

## Formulas esperadas
- Usuarios activos: `COUNT(*) FROM usuarios WHERE estado = 'ACTIVO'`
- Roles creados: `COUNT(*) FROM roles`
- Menus configurados: `COUNT(*) FROM menus`
- Accesos hoy: `COUNT(*) FROM log_accesos WHERE fecha_acceso = date('now')`
- Sesiones en linea: `COUNT(*) FROM sesiones WHERE estado = 'ACTIVA'`

## Integracion de estilo
Usar como base la hoja `assets/SKILL_ACCESOSMENUES.css`.
