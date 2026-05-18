# Contrato de la Plataforma

## Contexto comun

Toda app recibe como minimo:
- `usuario`
- `rol`
- `grupo`
- `portal_origen`
- `modulo_origen`
- `permisos`

## Reglas de integracion

- El portal corporativo decide que tablero abrir.
- Los tableros madre pueden ser llamados desde el menu central o de forma directa.
- El tablero debe adaptar su vista segun permisos.
- El acceso debe quedar auditado.

## Formato comun de datos

- Las fechas deben intercambiarse en ISO 8601.
- Los errores deben responder de forma uniforme:
  - `ok: false`
  - `error.code`
  - `error.message`
  - `error.details` opcional
- Los payloads compartidos deben mantener nombres estables entre SQLite y SQL Server.
- `TEXT` en desarrollo y `NVARCHAR` en produccion deben representar el mismo significado funcional.

## Auditoria minima

- `fecha_hora`
- `hora_inicio`
- `hora_fin`
- `duracion_segundos`
- `usuario_id`
- `rol_id`
- `portal_id`
- `modulo_id`
- `menu_id`

## Convenciones

- `portal-corporativo`: entrada principal
- `administracion-general`: gobierno de usuarios, menus y permisos
- `compras`, `produccion`, `inventario`, `finanzas`, `cxc`, `cxp`, `rrhh`, `reportes`: dominios funcionales
