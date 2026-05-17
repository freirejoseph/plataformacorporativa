# SKILL_portal-corporativo

## Proposito
Define el hub de entrada de la plataforma: resuelve identidad, consolida el menu maestro y enruta a los demas tableros.

## Alcance
- Resolver `usuario`, `rol`, `grupo`, `portal_origen` y `modulo_origen`.
- Mostrar accesos rapidos a tableros internos y sistemas externos.
- Centralizar el menu maestro y la navegacion de entrada.
- Registrar auditoria de acceso y redireccion.

## Debe contener
- contrato de entrada y salida entre tableros
- menu maestro y reglas de redireccion
- catalogo de integraciones y accesos externos
- reglas de acceso segun permisos
- trazabilidad de navegación

## Contexto obligatorio
- recibe `usuario`
- debe respetar permisos del portal madre
- no debe duplicar la logica de identidad de `accesos-menues`

## Salida esperada
- dashboard de entrada
- tarjetas de integracion
- accesos rapidos
- reglas de enrutamiento
