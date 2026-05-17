# SKILL_compras

## Proposito
Define el tablero de compras: proveedores, cotizaciones, ordenes, recepciones, aprobaciones y analisis de costos.

## Alcance
- Gestionar proveedores y contratos.
- Registrar cotizaciones, ordenes de compra y recepciones.
- Manejar aprobaciones y estados del flujo de compras.
- Analizar costo, cumplimiento y abastecimiento.

## Debe contener
- tablas principales de proveedores y compras
- relaciones con inventario y finanzas
- reglas de aprobacion y validacion
- permisos por rol y usuario
- integracion con reportes y alertas

## Contexto obligatorio
- recibe `usuario`
- debe respetar permisos del portal
- no debe exponer datos fuera del alcance del usuario

## Salida esperada
- estructura de datos
- endpoints o consultas base
- reglas de integracion con el portal principal
