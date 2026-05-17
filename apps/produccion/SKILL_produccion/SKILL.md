# SKILL_produccion

## Proposito
Define el tablero de produccion: ordenes, rutas, operaciones, consumo, eficiencia y trazabilidad.

## Alcance
- Gestionar ordenes de produccion y rutas.
- Registrar operaciones, consumos, scrap y paradas.
- Medir productividad, cumplimiento y eficiencia.
- Dar visibilidad a trazabilidad de planta.

## Debe contener
- tablas de ordenes, rutas y operaciones
- reglas de consumo y scrap
- permisos por rol
- integracion con inventario y reportes
- validaciones de produccion

## Contexto obligatorio
- recibe `usuario`
- debe respetar permisos del portal
- no debe exponer datos fuera del alcance del usuario

## Salida esperada
- estructura de datos
- endpoints o consultas base
- reglas de integracion con el portal principal
