# SKILL Portal Corporativo

## Objetivo
El **Portal Corporativo** es la primera pantalla que ve el usuario al entrar a la plataforma.
Su trabajo es autenticar, identificar al usuario y mostrar solo los accesos, tableros y gestiones
que le corresponden segun sus permisos.

Este portal no administra la seguridad. Esa funcion pertenece al subportal **accesos-menues**.

## Rol dentro de la plataforma
El Portal Corporativo es la capa de entrada y navegacion principal.

Flujo esperado:
1. El usuario abre el portal.
2. Inicia sesion.
3. El portal resuelve sus permisos, rol, grupo y contexto.
4. Se construye su menu de accesos.
5. Se muestran los tableros y gestiones autorizadas.
6. Cada tablero valida nuevamente el usuario y sus permisos.

## Subportal inicial
El primer subportal que se lanza desde aqui es:

- `accesos-menues`

Ese subportal es la madre de:
- usuarios
- roles
- grupos
- menus
- permisos
- auditoria
- sesiones

## Alcance funcional
El Portal Corporativo debe:
- mostrar un home ejecutivo con tarjetas de accesos
- listar los portales y tableros disponibles para el usuario
- permitir acceso directo a dashboards autorizados
- permitir acceso a gestiones autorizadas
- mostrar estado, notificaciones y accesos rapidos
- servir como hub de navegacion entre subportales

## Reglas de negocio
- Todo usuario debe entrar por este portal o por un tablero especifico con validacion de usuario.
- Ningun acceso debe mostrarse si no esta autorizado.
- Si el usuario entra directo a un tablero, el tablero debe validar permisos igualmente.
- Un usuario puede ver solo dashboards, o dashboards + gestiones, segun su perfil.
- Los permisos se resuelven por usuario, grupo y rol, respetando prioridad del contexto individual.

## Modelo visual
El portal debe seguir una estetica corporativa oscura, con:
- sidebar fija de navegacion
- header superior con busqueda, alertas y usuario
- tarjetas de accesos rapidos
- paneles de estado y actividad
- tipografia clara, contrastada y jerarquia fuerte

## Secciones sugeridas
- Inicio
- Portales principales
- Tableros disponibles
- Accesos rapidos
- Estado del sistema
- Notificaciones
- Usuario activo

## Relacion con `accesos-menues`
`accesos-menues` es el primer subportal vivo y debe abrirse desde el Portal Corporativo como:
- acceso directo
- tarjeta de lanzamiento
- opcion en menu

El Portal Corporativo no duplica la administracion de usuarios ni permisos.
Solo consume lo definido por `accesos-menues`.

## Artefactos asociados
- `docs/SKILLPortalCorporativo.css`
- `docs/SKILL_accesos-menues.md`
- `docs/SKILL_accesos-menues.css`
- `docs/stack-tecnico.md`

## Criterios de aceptacion
- El usuario reconoce el portal como su punto de entrada.
- Los accesos visibles coinciden con sus permisos.
- El subportal `accesos-menues` aparece como entrada principal.
- El diseno se mantiene coherente con el mockup corporativo.
- El portal puede crecer para hospedar mas subportales sin romper la estructura.

## Pendientes de implementacion
- autenticacion real del portal corporativo
- layout final del home de entrada
- resolver menu dinamico desde permisos
- integrar notificaciones y accesos por rol
- conectar el portal con los subportales operativos

## Frontend de referencia
El frontend del Portal Corporativo debe construirse siguiendo este contrato visual:
- `docs/SKILLPortalCorporativo.css`

El subportal inicial `accesos-menues` debe seguir su propio contrato:
- `docs/SKILL_accesos-menues.md`
- `docs/SKILL_accesos-menues.css`

Ambos documentos son la referencia central para maquetacion y comportamiento visual.

