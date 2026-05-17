# SKILL_cxc

## Proposito
Define el tablero de cuentas por cobrar: clientes, facturas, creditos, cobranzas, vencimientos y cartera.

## Alcance
- Administrar clientes y condiciones de cobro.
- Registrar facturas, notas de credito y cobranzas.
- Controlar vencimientos, aging y promesas de pago.
- Exponer cartera y riesgo por cliente.

## Debe contener
- tablas de clientes, facturas y cobranzas
- reglas de vencimiento y mora
- permisos por usuario y rol
- integracion con finanzas y reportes
- validaciones de saldo y estado

## Contexto obligatorio
- recibe `usuario`
- debe respetar permisos del portal
- no debe exponer datos fuera del alcance del usuario

## Salida esperada
- estructura de datos
- endpoints o consultas base
- reglas de integracion con el portal principal
