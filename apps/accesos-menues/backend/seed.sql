INSERT OR IGNORE INTO roles (codigo, nombre, descripcion, estado) VALUES
('SUPER_ADMIN', 'Super Administrador', 'Acceso total al sistema', 'ACTIVO'),
('ADMIN', 'Administrador', 'Administracion y configuracion', 'ACTIVO'),
('GERENTE', 'Gerente', 'Gestion general', 'ACTIVO'),
('CONTADOR', 'Contador', 'Finanzas y contabilidad', 'ACTIVO'),
('BASICO', 'Usuario Basico', 'Accesos limitados', 'ACTIVO'),
('INVITADO', 'Invitado', 'Solo lectura de reportes', 'ACTIVO');

INSERT OR IGNORE INTO grupos (codigo, nombre, descripcion, estado) VALUES
('GRP_ADMIN', 'Administracion', 'Usuarios administrativos', 'ACTIVO'),
('GRP_PLANTA', 'Planta', 'Usuarios de planta', 'ACTIVO'),
('GRP_FIN', 'Finanzas', 'Usuarios de finanzas', 'ACTIVO');

INSERT OR IGNORE INTO usuarios (nombre, correo, password_hash, cargo, estado, avatar_url, fecha_creacion, ultimo_acceso) VALUES
('Joseph', 'joseph@empresa.com', 'pbkdf2_sha256$200000$plataforma_salt_2026$f4a06886635cfa81332620c31cfb4058281b83484b5673042d4d5b35e2cae507', 'Gerente', 'ACTIVO', NULL, '2024-05-20 09:00:00', '2024-05-20 09:45:00'),
('Carlos Alberto', 'carlos.alberto@empresa.com', 'pbkdf2_sha256$200000$plataforma_salt_2026$f4a06886635cfa81332620c31cfb4058281b83484b5673042d4d5b35e2cae507', 'Administrador', 'ACTIVO', NULL, '2024-05-19 09:00:00', '2024-05-20 09:30:00'),
('Maria Jaramillo', 'maria.jaramillo@empresa.com', 'pbkdf2_sha256$200000$plataforma_salt_2026$f4a06886635cfa81332620c31cfb4058281b83484b5673042d4d5b35e2cae507', 'Contador', 'ACTIVO', NULL, '2024-05-19 09:00:00', '2024-05-20 08:50:00'),
('Juan Rodriguez', 'juan.rodriguez@empresa.com', 'pbkdf2_sha256$200000$plataforma_salt_2026$f4a06886635cfa81332620c31cfb4058281b83484b5673042d4d5b35e2cae507', 'Gerente de Planta', 'ACTIVO', NULL, '2024-05-19 09:00:00', '2024-05-20 08:15:00'),
('Luis Paredes', 'luis.paredes@empresa.com', 'pbkdf2_sha256$200000$plataforma_salt_2026$f4a06886635cfa81332620c31cfb4058281b83484b5673042d4d5b35e2cae507', 'Jefe de Produccion', 'ACTIVO', NULL, '2024-05-19 09:00:00', '2024-05-19 17:40:00'),
('Gabriel Fuentes', 'gabriel.fuentes@empresa.com', 'pbkdf2_sha256$200000$plataforma_salt_2026$f4a06886635cfa81332620c31cfb4058281b83484b5673042d4d5b35e2cae507', 'Encargado de Inventario', 'INACTIVO', NULL, '2024-05-10 09:00:00', '2024-05-10 11:10:00');

INSERT OR IGNORE INTO portales (codigo, nombre, tipo, url_base, estado) VALUES
('ACCESOS', 'Accesos y Menues', 'PORTAL', '/apps/accesos-menues/frontend/index.html', 'ACTIVO'),
('SYSPRO', 'SYSPRO ERP', 'ERP', 'https://syspro.local', 'ACTIVO'),
('ODOO_RRHH', 'Odoo RRHH', 'ERP', 'https://odoo.local', 'ACTIVO'),
('REPORTES', 'Portal Reportes', 'PORTAL', '/apps/reportes/frontend/index.html', 'ACTIVO'),
('COMPRAS', 'Portal Compras', 'PORTAL', '/apps/compras/frontend/index.html', 'ACTIVO');

INSERT OR IGNORE INTO modulos (portal_id, codigo, nombre, descripcion, icono, estado) VALUES
(1, 'ACCESOS_CORE', 'Accesos y Menues', 'Modulo madre', 'lock', 'ACTIVO'),
(2, 'SYSPRO_PROD', 'Produccion', 'Modulo de produccion', 'factory', 'ACTIVO'),
(2, 'SYSPRO_INV', 'Inventario', 'Modulo de inventario', 'box', 'ACTIVO'),
(4, 'REPORTES_CORE', 'Reportes Corporativos', 'Indicadores y analitica', 'chart', 'ACTIVO');

INSERT OR IGNORE INTO menus (portal_id, modulo_id, menu_padre_id, codigo, nombre, icono, orden, estado) VALUES
(1, 1, NULL, 'MENU_DASH', 'Dashboard', 'dashboard', 1, 'ACTIVO'),
(1, 1, NULL, 'MENU_USUARIOS', 'Usuarios y Accesos', 'users', 2, 'ACTIVO'),
(1, 1, NULL, 'MENU_ROLES', 'Roles y Permisos', 'shield', 3, 'ACTIVO'),
(1, 1, NULL, 'MENU_GRUPOS', 'Grupos', 'group', 4, 'ACTIVO'),
(1, 1, NULL, 'MENU_PORTALES', 'Portales y Modulos', 'portal', 5, 'ACTIVO'),
(1, 1, NULL, 'MENU_AUDIT', 'Auditoria', 'audit', 6, 'ACTIVO');

INSERT OR IGNORE INTO opciones_programa (menu_id, codigo, nombre, tipo, url, componente, abre_nueva_pestana, requiere_log, estado) VALUES
(1, 'OP_DASH', 'Ver Dashboard', 'COMPONENTE', '/apps/accesos-menues/frontend/index.html', 'dashboard', 0, 1, 'ACTIVO'),
(2, 'OP_USERS', 'Gestion de Usuarios', 'COMPONENTE', '/apps/accesos-menues/frontend/index.html#usuarios', 'usuarios', 0, 1, 'ACTIVO'),
(3, 'OP_ROLES', 'Gestion de Roles', 'COMPONENTE', '/apps/accesos-menues/frontend/index.html#roles', 'roles', 0, 1, 'ACTIVO'),
(4, 'OP_GROUPS', 'Gestion de Grupos', 'COMPONENTE', '/apps/accesos-menues/frontend/index.html#grupos', 'grupos', 0, 1, 'ACTIVO'),
(5, 'OP_PORTALS', 'Gestion de Portales', 'COMPONENTE', '/apps/accesos-menues/frontend/index.html#portales', 'portales', 0, 1, 'ACTIVO'),
(6, 'OP_AUDIT', 'Ver Auditoria', 'COMPONENTE', '/apps/accesos-menues/frontend/index.html#auditoria', 'auditoria', 0, 1, 'ACTIVO');

INSERT OR IGNORE INTO usuarios_roles (usuario_id, rol_id) VALUES
(1, 1),
(2, 2),
(3, 4),
(4, 3),
(5, 5),
(6, 6);

INSERT OR IGNORE INTO usuarios_grupos (usuario_id, grupo_id) VALUES
(1, 1),
(2, 1),
(3, 3),
(4, 2),
(5, 2),
(6, 2);

INSERT OR IGNORE INTO permisos_rol (rol_id, opcion_id, permiso) VALUES
(1, 1, 'PERMITIDO'),
(1, 2, 'PERMITIDO'),
(1, 3, 'PERMITIDO'),
(1, 4, 'PERMITIDO'),
(1, 5, 'PERMITIDO'),
(1, 6, 'PERMITIDO'),
(2, 1, 'PERMITIDO'),
(2, 2, 'PERMITIDO'),
(2, 3, 'PERMITIDO'),
(2, 4, 'PERMITIDO'),
(2, 5, 'PERMITIDO'),
(2, 6, 'PERMITIDO'),
(3, 1, 'PERMITIDO'),
(3, 2, 'PERMITIDO'),
(3, 3, 'PERMITIDO'),
(3, 4, 'PERMITIDO'),
(3, 5, 'SOLO_LECTURA'),
(3, 6, 'PERMITIDO'),
(4, 1, 'PERMITIDO'),
(4, 2, 'PERMITIDO'),
(4, 3, 'PERMITIDO'),
(4, 4, 'SOLO_LECTURA'),
(4, 5, 'DENEGADO'),
(4, 6, 'PERMITIDO'),
(5, 1, 'SOLO_LECTURA'),
(5, 2, 'PERMITIDO'),
(5, 3, 'DENEGADO'),
(5, 4, 'DENEGADO'),
(5, 5, 'DENEGADO'),
(5, 6, 'DENEGADO'),
(6, 1, 'SOLO_LECTURA');

INSERT OR IGNORE INTO log_actividad (usuario_id, fecha_hora, accion, detalle, ip, equipo) VALUES
(1, datetime('now', '-45 minutes'), 'Inicio de sesion', 'Inicio de sesion exitoso', '192.168.1.10', 'PC-CA01'),
(2, datetime('now', '-40 minutes'), 'Creacion de usuario', 'Se creo el usuario ana.gomez', '192.168.1.10', 'PC-CA01'),
(3, datetime('now', '-35 minutes'), 'Cambio de permisos', 'Se actualizaron permisos del rol Contador', '192.168.1.15', 'PC-MJ01'),
(4, datetime('now', '-30 minutes'), 'Acceso a modulo', 'Accedio al modulo Produccion', '192.168.1.22', 'PC-JR01'),
(5, datetime('now', '-25 minutes'), 'Respaldo automatico', 'Respaldo de seguridad completado', '192.168.1.11', 'SRV-APP-01'),
(1, datetime('now', '-20 minutes'), 'Asignacion de rol', 'Rol asignado: Jefe de Produccion', '192.168.1.18', 'PC-LP01');

INSERT OR IGNORE INTO sesiones (usuario_id, inicio, fin, estado, ip, equipo, navegador) VALUES
(1, datetime('now', '-90 minutes'), NULL, 'ACTIVA', '192.168.1.10', 'PC-CA01', 'Chrome'),
(2, datetime('now', '-85 minutes'), NULL, 'ACTIVA', '192.168.1.10', 'PC-CA01', 'Chrome'),
(3, datetime('now', '-75 minutes'), datetime('now', '-10 minutes'), 'CERRADA', '192.168.1.15', 'PC-MJ01', 'Edge'),
(4, datetime('now', '-65 minutes'), NULL, 'ACTIVA', '192.168.1.22', 'PC-JR01', 'Firefox');

INSERT OR IGNORE INTO log_accesos (usuario_id, rol_id, portal_id, modulo_id, menu_id, opcion_id, programa_nombre, programa_url, fecha_acceso, hora_inicio, hora_fin, duracion_segundos, estado, ip, equipo, navegador, mensaje_error) VALUES
(1, 1, 1, 1, 1, 1, 'Dashboard', '/apps/accesos-menues/frontend/index.html', date('now'), time('now', '-45 minutes'), time('now', '-43 minutes'), 120, 'EXITOSO', '192.168.1.10', 'PC-CA01', 'Chrome', NULL),
(2, 2, 1, 1, 2, 2, 'Gestion de Usuarios', '/apps/accesos-menues/frontend/index.html#usuarios', date('now'), time('now', '-40 minutes'), time('now', '-39 minutes'), 75, 'EXITOSO', '192.168.1.10', 'PC-CA01', 'Chrome', NULL),
(3, 4, 1, 1, 3, 3, 'Gestion de Roles', '/apps/accesos-menues/frontend/index.html#roles', date('now'), time('now', '-35 minutes'), time('now', '-34 minutes'), 55, 'EXITOSO', '192.168.1.15', 'PC-MJ01', 'Edge', NULL);
