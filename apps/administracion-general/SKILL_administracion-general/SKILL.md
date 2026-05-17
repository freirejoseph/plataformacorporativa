# SKILL_administracion-general

## Proposito
Define el tablero de gobierno corporativo, parametros globales, licencias, politicas y mantenimiento transversal.

## Alcance
- Gestionar parametros globales y catlogos comunes.
- Administrar politicas, licencias y configuracion transversal.
- Exponer mantenimientos que no pertenecen a identidad ni navegacion.
- Consumir contexto de seguridad desde `accesos-menues` sin replicarlo.

## Debe contener
- alcance funcional de gobierno
- tablas de parametros y configuracion
- reglas de negocio y validaciones
- permisos o roles aplicables
- integracion con el portal madre

## Contexto obligatorio
- recibe `usuario`
- debe respetar permisos del portal
- no debe duplicar usuarios, roles ni permisos de `accesos-menues`

## Salida esperada
- estructura de datos
- endpoints o consultas base
- reglas de integracion con el portal principal
