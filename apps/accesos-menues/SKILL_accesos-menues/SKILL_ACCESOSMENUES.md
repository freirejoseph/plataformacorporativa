# SKILL_ACCESOSMENUES.md

## 1. Nombre del Skill

**SKILL_ACCESOSMENUES**  
Skill para construir el **Portal de Administración de Usuarios, Menús, Roles, Permisos y Auditoría de Accesos**.

Este Skill debe ser usado por el agente de programación para generar una aplicación web local que permita:

- Crear usuarios.
- Crear roles.
- Crear grupos.
- Crear portales y módulos.
- Construir menús dinámicos.
- Crear opciones finales que abren programas, portales, reportes o URLs.
- Asignar accesos por usuario, rol o grupo.
- Registrar auditoría de inicio y fin de uso de cada programa.
- Consultar logs de accesos, errores y actividad administrativa.

---

## 2. Objetivo general

Crear un portal administrativo que funcione como **centro de seguridad, accesos y navegación corporativa**.

El portal no debe depender inicialmente de SQL Server ni de una base empresarial externa. La base de datos inicial debe ser local, ubicada en la raíz del proyecto, para facilitar pruebas, despliegue rápido y operación independiente.

---

## 3. Concepto funcional

El sistema debe trabajar con esta lógica:

```text
Usuario
   ↓
Login / Autenticación
   ↓
Rol / Grupo / Permisos directos
   ↓
Menú permitido
   ↓
Opción final del menú
   ↓
Ejecución de portal, programa, reporte o URL
   ↓
Registro de log de acceso
   ↓
Registro de hora de inicio, hora fin, duración, estado, IP y equipo
```

---

## 4. Base de datos local recomendada

### Opción recomendada: SQLite

Usar **SQLite** como base local principal.

Archivo sugerido:

```text
/portal-data/accesos_menues.sqlite
```

### Razones

- No requiere instalar motor SQL externo.
- Funciona como archivo local.
- Es ideal para prototipos, portales administrativos y aplicaciones internas.
- Soporta transacciones.
- Puede migrarse posteriormente a SQL Server, PostgreSQL o MySQL.
- Se integra muy bien con Node.js, Python, .NET y Electron.

### Alternativas posibles

| Base local | Uso recomendado |
|---|---|
| SQLite | Recomendado para producción local inicial |
| DuckDB | Bueno para analítica local y tableros pesados |
| JSON local | Solo para prototipo simple, no recomendado para seguridad |
| LiteDB | Recomendado si el backend será .NET |
| IndexedDB | Solo para datos en navegador, no para seguridad central |

### Recomendación final

Para este portal usar:

```text
SQLite + Prisma ORM o Drizzle ORM
```

Si el backend será Node.js:

```text
better-sqlite3 + Drizzle ORM
```

Si el backend será .NET:

```text
SQLite + Entity Framework Core
```

---

## 5. Metodología de construcción

### Fase 1 — Diseño de estructura base

Crear primero la estructura visual y navegación:

- Menú lateral.
- Header superior.
- KPIs administrativos.
- Grilla de usuarios.
- Panel de roles.
- Matriz de permisos.
- Actividad reciente.
- Acciones rápidas.

### Fase 2 — Modelo de datos local

Crear tablas locales en SQLite.

### Fase 3 — Administración de catálogos

Crear mantenimiento para:

- Usuarios.
- Roles.
- Grupos.
- Portales.
- Módulos.
- Menús.
- Opciones/programas.

### Fase 4 — Asignación de permisos

Permitir asignar accesos por:

- Usuario.
- Rol.
- Grupo.
- Portal.
- Módulo.
- Opción final.

### Fase 5 — Ejecución y auditoría

Cada vez que el usuario abra una opción final, se debe registrar:

- Usuario.
- Programa.
- Hora inicio.
- Hora fin.
- Duración.
- Estado.
- IP.
- Equipo.
- Navegador.

### Fase 6 — Reportes administrativos

Crear vistas para:

- Usuarios activos.
- Roles creados.
- Módulos disponibles.
- Sesiones activas.
- Portales conectados.
- Logs de acceso.
- Errores.
- Actividad reciente.

---

## 6. Componentes visuales del tablero

### 6.1 Layout principal

| Objeto visual | Nombre técnico | Función |
|---|---|---|
| Contenedor global | `LayoutAccesosMenues` | Estructura general de pantalla |
| Barra lateral | `MenuLateralPrincipal` | Navegación principal |
| Cabecera superior | `HeaderAdministracionAccesos` | Título, búsqueda, usuario y alertas |
| Área de contenido | `PanelContenidoPrincipal` | Contenedor de KPIs, tablas y paneles |
| Pie de página | `FooterSistemaAccesos` | Estado, usuario, rol y versión |

---

## 7. Menú lateral

### Objeto principal

`MenuLateralPrincipal`

### Función

Permite navegar por todos los módulos de administración.

| Opción visual | Nombre técnico | Función |
|---|---|---|
| Logo SYSPRO | `LogoSysproERP` | Identidad del ERP base |
| Dashboard | `MenuDashboard` | Acceso al resumen principal |
| Usuarios y Accesos | `MenuUsuariosAccesos` | Administración de usuarios y permisos |
| Roles y Permisos | `MenuRolesPermisos` | Administración de roles |
| Grupos | `MenuGruposSeguridad` | Administración de grupos |
| Portales y Módulos | `MenuPortalesModulos` | Catálogo de portales conectados |
| Seguridad | `MenuSeguridad` | Políticas de seguridad |
| Políticas de Acceso | `MenuPoliticasAcceso` | Reglas de acceso |
| Auditoría | `MenuAuditoria` | Consulta de logs |
| SYSPRO ERP | `MenuModuloSysproERP` | Accesos a módulos SYSPRO |
| Odoo RRHH | `MenuModuloOdooRRHH` | Accesos a RRHH en Odoo |
| Tableros Interactivos | `MenuTablerosInteractivos` | Accesos a dashboards propios |
| Integraciones | `MenuIntegraciones` | APIs y conectores |
| Documentos | `MenuDocumentos` | Documentos y archivos |
| Parámetros Generales | `MenuParametrosGenerales` | Parámetros del portal |
| Notificaciones | `MenuNotificaciones` | Alertas del sistema |
| Respaldo y Recuperación | `MenuRespaldos` | Copias de seguridad |
| Licencias | `MenuLicencias` | Control licencias internas |
| Logo PESA | `LogoPesaModulo` | Logo decorativo dentro de barra lateral |
| Cerrar sesión | `BotonCerrarSesion` | Logout seguro |

---

## 8. Header superior

### Objeto

`HeaderAdministracionAccesos`

| Elemento | Nombre técnico | Función |
|---|---|---|
| Botón menú | `BotonColapsarMenu` | Contrae o expande barra lateral |
| Título pantalla | `TituloAdministracionAccesos` | Nombre del módulo activo |
| Subtítulo | `SubtituloAdministracionAccesos` | Descripción funcional |
| Buscador global | `BuscadorGlobalAccesos` | Busca usuarios, roles, portales y permisos |
| Notificaciones | `IconoNotificacionesAccesos` | Alertas pendientes |
| Seguridad | `IconoSeguridadHeader` | Estado de seguridad |
| Ayuda | `IconoAyudaHeader` | Manual o soporte |
| Avatar usuario | `AvatarUsuarioActivo` | Foto del usuario conectado |
| Nombre usuario | `TextoUsuarioActivo` | Nombre del usuario conectado |
| Cargo usuario | `TextoCargoUsuarioActivo` | Cargo o rol visible |
| Logo Accesos Digitales | `LogoAccesosDigitalesHeader` | Identidad del portal, ubicado arriba derecha |

---

## 9. KPIs administrativos

### Contenedor

`PanelKPIAdministracionAccesos`

| KPI | Nombre técnico | Función |
|---|---|---|
| Usuarios Totales | `KPIUsuariosTotales` | Cantidad total de usuarios registrados |
| Roles Creados | `KPIRolesCreados` | Cantidad total de roles configurados |
| Módulos Disponibles | `KPIModulosDisponibles` | Total de módulos habilitados |
| Sesiones Activas | `KPISesionesActivas` | Usuarios conectados actualmente |
| Portales Conectados | `KPIPortalesConectados` | Portales disponibles y operativos |
| Fecha y Hora | `KPIFechaHoraSistema` | Fecha y hora del sistema |

### Reglas UX de KPI

- Cada KPI debe tener icono.
- Cada KPI debe mostrar valor principal grande.
- Cada KPI debe mostrar detalle secundario.
- Cada KPI debe mostrar una mini tendencia tipo sparkline cuando aplique.
- Usar colores consistentes:
  - Azul: usuarios / información.
  - Verde: activo / permitido / correcto.
  - Morado: módulos / seguridad.
  - Naranja: sesiones / llaves / acciones.
  - Cyan: portales / conectividad.

---

## 10. Panel Usuarios del Sistema

### Objeto

`PanelUsuariosSistema`

### Función

Muestra y administra los usuarios registrados.

| Elemento | Nombre técnico | Función |
|---|---|---|
| Título panel | `TituloUsuariosSistema` | Identifica sección |
| Buscador usuario | `InputBuscarUsuario` | Filtra usuarios |
| Filtro estado | `SelectEstadoUsuario` | Activo, inactivo, todos |
| Botón filtro avanzado | `BotonFiltroUsuarios` | Abre filtros adicionales |
| Botón nuevo usuario | `BotonNuevoUsuario` | Crea usuario |
| Tabla usuarios | `GridUsuariosSistema` | Lista usuarios |
| Paginador usuarios | `PaginadorUsuarios` | Navega páginas |

### Columnas de tabla

| Columna | Nombre técnico | Función |
|---|---|---|
| Usuario | `ColUsuarioNombre` | Nombre corto y avatar |
| Correo electrónico | `ColUsuarioCorreo` | Email del usuario |
| Rol | `ColUsuarioRol` | Rol asignado |
| Portal asignado | `ColUsuarioPortalAsignado` | Portal principal asignado |
| Estado | `ColUsuarioEstado` | Activo / Inactivo |
| Último acceso | `ColUsuarioUltimoAcceso` | Última fecha/hora de ingreso |
| Acciones | `ColUsuarioAcciones` | Editar, inactivar, permisos, ver logs |

---

## 11. Panel Roles del Sistema

### Objeto

`PanelRolesSistema`

### Función

Administra roles y permite ver cantidad de usuarios por rol.

| Elemento | Nombre técnico | Función |
|---|---|---|
| Lista roles | `ListaRolesSistema` | Muestra roles disponibles |
| Botón nuevo rol | `BotonNuevoRol` | Crea rol |
| Item rol | `ItemRolSistema` | Tarjeta por rol |
| Ver todos roles | `BotonVerTodosRoles` | Abre mantenimiento completo |

### Roles sugeridos iniciales

- `SuperAdministrador`
- `Administrador`
- `GerentePlanta`
- `JefeProduccion`
- `Contador`
- `EncargadoInventario`
- `UsuarioBasico`
- `Invitado`

---

## 12. Matriz de Permisos por Portal y Módulo

### Objeto

`PanelMatrizPermisosPortalModulo`

### Función

Permite ver de forma cruzada qué rol tiene acceso a cada módulo o portal.

### Estados de permiso

| Estado | Nombre técnico | Significado |
|---|---|---|
| Permitido | `EstadoPermisoPermitido` | Puede acceder |
| Solo lectura | `EstadoPermisoSoloLectura` | Puede consultar, no modificar |
| Denegado | `EstadoPermisoDenegado` | No puede acceder |

### Columnas sugeridas

- `ColPermisoModuloPortal`
- `ColPermisoSysproERP`
- `ColPermisoOdooRRHH`
- `ColPermisoPortalReportes`
- `ColPermisoPortalCompras`
- `ColPermisoPortalCalidad`

### Filas sugeridas

- Producción
- Inventario
- Finanzas
- CxC
- CxP
- Compras
- Costos
- Planeación
- Empleados
- Nómina
- Asistencia
- Solicitudes
- Documentos

---

## 13. Panel Actividad Reciente

### Objeto

`PanelActividadReciente`

### Función

Muestra eventos recientes administrativos y de acceso.

| Columna | Nombre técnico | Función |
|---|---|---|
| Fecha y hora | `ColActividadFechaHora` | Momento del evento |
| Usuario | `ColActividadUsuario` | Usuario que ejecutó acción |
| Acción | `ColActividadAccion` | Tipo de acción |
| Detalle | `ColActividadDetalle` | Descripción |
| IP | `ColActividadIP` | IP o equipo |

### Eventos a registrar

- Inicio de sesión.
- Cierre de sesión.
- Creación de usuario.
- Cambio de permisos.
- Asignación de rol.
- Acceso a módulo.
- Error de acceso.
- Cambio de contraseña.
- Respaldo automático.

---

## 14. Panel Acciones Rápidas

### Objeto

`PanelAccionesRapidas`

### Función

Permite ejecutar acciones administrativas frecuentes.

| Acción | Nombre técnico | Función |
|---|---|---|
| Crear usuario | `BotonCrearUsuario` | Abre formulario usuario |
| Crear rol | `BotonCrearRol` | Abre formulario rol |
| Asignar permisos | `BotonAsignarPermisos` | Abre asistente de permisos |
| Asignar accesos a portal | `BotonAsignarAccesosPortal` | Asigna módulos a usuario/rol |
| Importar usuarios | `BotonImportarUsuarios` | Carga usuarios desde archivo |
| Grupos | `BotonAdministrarGrupos` | Administra grupos |
| Políticas de acceso | `BotonPoliticasAcceso` | Reglas de seguridad |
| Auditoría | `BotonAuditoria` | Consulta logs |
| Respaldos | `BotonRespaldos` | Copia seguridad local |
| Configuración | `BotonConfiguracion` | Parámetros generales |

---

## 15. Constructor de Menús

### Pantalla requerida

`PantallaConstructorMenus`

### Objetivo

Crear la estructura dinámica de navegación del portal.

### Campos de menú

| Campo | Nombre técnico | Tipo |
|---|---|---|
| ID menú | `MenuId` | entero |
| Menú padre | `MenuPadreId` | entero nullable |
| Nombre visible | `MenuNombre` | texto |
| Código interno | `MenuCodigo` | texto único |
| Icono | `MenuIcono` | texto |
| Orden | `MenuOrden` | entero |
| Estado | `MenuEstado` | activo/inactivo |
| Portal origen | `MenuPortalId` | entero |

### Tipos de opción final

| Tipo | Nombre técnico | Uso |
|---|---|---|
| URL externa | `TipoOpcionURLExterna` | Abre web externa |
| URL interna | `TipoOpcionURLInterna` | Abre portal interno |
| Componente React | `TipoOpcionComponenteReact` | Carga componente interno |
| Reporte interactivo | `TipoOpcionReporteInteractivo` | Abre dashboard propio |
| API proceso | `TipoOpcionAPIProceso` | Ejecuta endpoint |
| Archivo/documento | `TipoOpcionDocumento` | Abre archivo |
| Sistema externo | `TipoOpcionSistemaExterno` | Abre SYSPRO/Odoo/otro |

---

## 16. Seguridad y permisos

### Modelo recomendado

Usar esquema RBAC con permisos directos.

```text
RBAC = Role Based Access Control
```

### Niveles

1. Permiso por rol.
2. Permiso por grupo.
3. Permiso directo por usuario.
4. Denegación explícita tiene prioridad sobre permitido.

### Regla de prioridad

```text
Denegado directo usuario
   > Permitido directo usuario
   > Denegado por grupo
   > Permitido por grupo
   > Denegado por rol
   > Permitido por rol
   > Sin acceso
```

---

## 17. Auditoría de ejecución de programas

Cada vez que un usuario ejecuta una opción final, crear registro en `LogAccesos`.

### Flujo

```text
1. Usuario presiona opción del menú.
2. Sistema valida permiso.
3. Si no tiene permiso, registra intento denegado.
4. Si tiene permiso, registra hora_inicio.
5. Abre el programa, portal o reporte.
6. Al cerrar o salir, registra hora_fin.
7. Calcula duración.
8. Registra estado final.
```

### Campos mínimos del log

- `LogId`
- `UsuarioId`
- `RolId`
- `PortalId`
- `ModuloId`
- `MenuId`
- `OpcionId`
- `ProgramaNombre`
- `ProgramaURL`
- `FechaAcceso`
- `HoraInicio`
- `HoraFin`
- `DuracionSegundos`
- `Estado`
- `IP`
- `Equipo`
- `Navegador`
- `MensajeError`

---

## 18. Modelo de datos SQLite sugerido

```sql
CREATE TABLE usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  correo TEXT NOT NULL UNIQUE,
  cargo TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO',
  avatar_url TEXT,
  fecha_creacion TEXT NOT NULL,
  ultimo_acceso TEXT
);

CREATE TABLE roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE usuario_roles (
  usuario_id INTEGER NOT NULL,
  rol_id INTEGER NOT NULL,
  PRIMARY KEY (usuario_id, rol_id)
);

CREATE TABLE grupos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE usuario_grupos (
  usuario_id INTEGER NOT NULL,
  grupo_id INTEGER NOT NULL,
  PRIMARY KEY (usuario_id, grupo_id)
);

CREATE TABLE portales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  tipo TEXT NOT NULL,
  url_base TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE modulos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  portal_id INTEGER NOT NULL,
  codigo TEXT NOT NULL,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  icono TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE menus (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  portal_id INTEGER,
  modulo_id INTEGER,
  menu_padre_id INTEGER,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  icono TEXT,
  orden INTEGER DEFAULT 0,
  estado TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE opciones_programa (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  menu_id INTEGER NOT NULL,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  tipo TEXT NOT NULL,
  url TEXT,
  componente TEXT,
  abre_nueva_pestana INTEGER DEFAULT 0,
  requiere_log INTEGER DEFAULT 1,
  estado TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE permisos_rol (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rol_id INTEGER NOT NULL,
  opcion_id INTEGER NOT NULL,
  permiso TEXT NOT NULL,
  UNIQUE (rol_id, opcion_id)
);

CREATE TABLE permisos_usuario (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id INTEGER NOT NULL,
  opcion_id INTEGER NOT NULL,
  permiso TEXT NOT NULL,
  UNIQUE (usuario_id, opcion_id)
);

CREATE TABLE permisos_grupo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  grupo_id INTEGER NOT NULL,
  opcion_id INTEGER NOT NULL,
  permiso TEXT NOT NULL,
  UNIQUE (grupo_id, opcion_id)
);

CREATE TABLE log_accesos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id INTEGER,
  rol_id INTEGER,
  portal_id INTEGER,
  modulo_id INTEGER,
  menu_id INTEGER,
  opcion_id INTEGER,
  programa_nombre TEXT,
  programa_url TEXT,
  fecha_acceso TEXT,
  hora_inicio TEXT,
  hora_fin TEXT,
  duracion_segundos INTEGER,
  estado TEXT,
  ip TEXT,
  equipo TEXT,
  navegador TEXT,
  mensaje_error TEXT
);

CREATE TABLE log_actividad (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id INTEGER,
  fecha_hora TEXT NOT NULL,
  accion TEXT NOT NULL,
  detalle TEXT,
  ip TEXT,
  equipo TEXT
);
```

---

## 19. Endpoints sugeridos

```text
GET    /api/dashboard/resumen
GET    /api/usuarios
POST   /api/usuarios
PUT    /api/usuarios/:id
GET    /api/roles
POST   /api/roles
GET    /api/menus/tree
POST   /api/menus
PUT    /api/menus/:id
GET    /api/opciones
POST   /api/opciones
POST   /api/permisos/asignar
GET    /api/permisos/matriz
POST   /api/log-accesos/inicio
POST   /api/log-accesos/fin
GET    /api/log-accesos
GET    /api/log-actividad
```

---

## 20. Reglas de diseño visual

- Tema oscuro empresarial.
- Fondo principal azul negro.
- Cards con bordes suaves y transparencias.
- Íconos lineales blancos/azules.
- Estados con colores consistentes:
  - Verde: activo / permitido.
  - Amarillo: solo lectura / advertencia.
  - Rojo: denegado / error / inactivo.
  - Azul: información / navegación.
  - Morado: seguridad / módulos.
- Logo SYSPRO arriba izquierda.
- Logo Accesos Digitales arriba derecha.
- Logo PESA solo gráfico dentro del menú lateral, encima de cerrar sesión.
- Usuario visible: Joseph.
- Cargo visible: Gerente.

---

## 21. Criterios de aceptación

El agente de programación debe entregar una primera versión funcional que cumpla:

- El dashboard se ve similar al mockup entregado.
- El menú lateral funciona.
- Se pueden listar usuarios.
- Se pueden crear usuarios.
- Se pueden crear roles.
- Se pueden crear portales.
- Se pueden crear menús y submenús.
- Se pueden crear opciones finales.
- Se pueden asignar permisos.
- Se puede consultar matriz de permisos.
- Se registra log cuando se abre una opción.
- Se registra hora fin al cerrar una opción.
- La base local SQLite queda dentro de la raíz del proyecto.
- El diseño usa la hoja `SKILL_ACCESOSMENUES.css`.

---

## 22. Archivos esperados

```text
/SKILL_ACCESOSMENUES.md
/SKILL_ACCESOSMENUES.css
/portal-data/accesos_menues.sqlite
/src
  /components
  /pages
  /services
  /database
  /assets
```

---

## 23. Nota para el programador

Este Skill no es solo una pantalla. Es la base de un **framework interno de navegación corporativa**, donde cada nuevo portal, programa, reporte o dashboard se registra como una opción administrable y auditable.

El portal debe permitir que la empresa crezca sin tener que modificar código por cada nuevo acceso. El administrador debe poder crear menús y asignar accesos desde la interfaz.
