# SKILL_inventario

## Proposito
Define el tablero de inventario: items, bodegas, kardex, movimientos, stock minimo y valorizacion.

## Alcance
- Administrar articulos, bodegas y ubicaciones.
- Registrar entradas, salidas y transferencias.
- Controlar stock minimo y cobertura.
- Valorar existencias y alertar quiebres.

## Debe contener
- tablas de items, bodegas y movimientos
- reglas de stock y reposicion
- permisos por rol
- integracion con compras y produccion
- validaciones de inventario

## Contexto obligatorio
- recibe `usuario`
- debe respetar permisos del portal
- no debe exponer datos fuera del alcance del usuario

## Salida esperada
- estructura de datos
- endpoints o consultas base
- reglas de integracion con el portal principal
