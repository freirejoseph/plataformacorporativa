# Contrato de la Plataforma

## Contexto comun

Toda app recibe como minimo:
- `usuario`
- `rol`
- `portal_origen`
- `modulo_origen`
- `permisos`

## Reglas de integracion

- El portal corporativo decide que tablero abrir.
- Los tableros madre pueden ser llamados desde el menu central o de forma directa.
- El tablero debe adaptar su vista segun permisos.
- El acceso debe quedar auditado.

## Convenciones

- `portal-corporativo`: entrada principal
- `administracion-general`: gobierno de usuarios, menus y permisos
- `compras`, `produccion`, `inventario`, `finanzas`, `cxc`, `cxp`, `rrhh`, `reportes`: dominios funcionales
