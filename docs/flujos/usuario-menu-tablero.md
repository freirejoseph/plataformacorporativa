# Flujo Usuario -> Menu -> Tablero

## Objetivo

Definir el comportamiento comun para todos los tableros de la plataforma.

## Flujo

1. El usuario inicia sesion o entra por URL directa.
2. El sistema recibe el parametro `usuario`.
3. Se valida identidad y estado.
4. Se consultan roles, permisos y accesos.
5. Se construye el menu visible para ese usuario.
6. Se determina el tablero o subtablero a mostrar.
7. El tablero carga datos filtrados por usuario, rol y alcance.
8. Se registra auditoria de ingreso y acciones.

## Reglas

- Ningun tablero debe asumir acceso libre.
- Ningun tablero debe mostrar opciones no autorizadas.
- Cada modulo puede vivir por separado, pero debe respetar el mismo contrato de identidad.
- El menu central puede redirigir a portales internos, tableros madre o vistas especificas.
