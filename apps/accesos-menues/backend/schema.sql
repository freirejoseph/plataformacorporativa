PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  correo TEXT NOT NULL UNIQUE,
  password_hash TEXT,
  cargo TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO',
  avatar_url TEXT,
  fecha_creacion TEXT NOT NULL,
  ultimo_acceso TEXT
);

CREATE TABLE IF NOT EXISTS roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS grupos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS usuarios_roles (
  usuario_id INTEGER NOT NULL,
  rol_id INTEGER NOT NULL,
  PRIMARY KEY (usuario_id, rol_id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS usuarios_grupos (
  usuario_id INTEGER NOT NULL,
  grupo_id INTEGER NOT NULL,
  PRIMARY KEY (usuario_id, grupo_id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS portales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  tipo TEXT NOT NULL,
  url_base TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS modulos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  portal_id INTEGER NOT NULL,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  descripcion TEXT,
  icono TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVO',
  FOREIGN KEY (portal_id) REFERENCES portales(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS menus (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  portal_id INTEGER,
  modulo_id INTEGER,
  menu_padre_id INTEGER,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  icono TEXT,
  orden INTEGER DEFAULT 0,
  estado TEXT NOT NULL DEFAULT 'ACTIVO',
  FOREIGN KEY (portal_id) REFERENCES portales(id) ON DELETE SET NULL,
  FOREIGN KEY (modulo_id) REFERENCES modulos(id) ON DELETE SET NULL,
  FOREIGN KEY (menu_padre_id) REFERENCES menus(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS opciones_programa (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  menu_id INTEGER NOT NULL,
  codigo TEXT NOT NULL UNIQUE,
  nombre TEXT NOT NULL,
  tipo TEXT NOT NULL,
  url TEXT,
  componente TEXT,
  abre_nueva_pestana INTEGER DEFAULT 0,
  requiere_log INTEGER DEFAULT 1,
  estado TEXT NOT NULL DEFAULT 'ACTIVO',
  FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS permisos_rol (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rol_id INTEGER NOT NULL,
  opcion_id INTEGER NOT NULL,
  permiso TEXT NOT NULL,
  UNIQUE (rol_id, opcion_id),
  FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
  FOREIGN KEY (opcion_id) REFERENCES opciones_programa(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS permisos_usuario (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id INTEGER NOT NULL,
  opcion_id INTEGER NOT NULL,
  permiso TEXT NOT NULL,
  UNIQUE (usuario_id, opcion_id),
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  FOREIGN KEY (opcion_id) REFERENCES opciones_programa(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS permisos_grupo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  grupo_id INTEGER NOT NULL,
  opcion_id INTEGER NOT NULL,
  permiso TEXT NOT NULL,
  UNIQUE (grupo_id, opcion_id),
  FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
  FOREIGN KEY (opcion_id) REFERENCES opciones_programa(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS log_accesos (
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

CREATE TABLE IF NOT EXISTS sesiones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id INTEGER NOT NULL,
  inicio TEXT NOT NULL,
  fin TEXT,
  estado TEXT NOT NULL DEFAULT 'ACTIVA',
  ip TEXT,
  equipo TEXT,
  navegador TEXT,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS log_actividad (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id INTEGER,
  fecha_hora TEXT NOT NULL,
  accion TEXT NOT NULL,
  detalle TEXT,
  ip TEXT,
  equipo TEXT
);

CREATE INDEX IF NOT EXISTS idx_log_accesos_fecha_acceso ON log_accesos(fecha_acceso);
CREATE INDEX IF NOT EXISTS idx_log_actividad_fecha_hora ON log_actividad(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_usuarios_roles_rol_id ON usuarios_roles(rol_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_grupos_grupo_id ON usuarios_grupos(grupo_id);
CREATE INDEX IF NOT EXISTS idx_sesiones_usuario_id ON sesiones(usuario_id);
