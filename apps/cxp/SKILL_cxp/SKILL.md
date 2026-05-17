# SKILL_cxp

## Proposito
Define el tablero de cuentas por pagar: proveedores, facturas, pagos, retenciones, aprobaciones y flujo de caja.

## Alcance
- Administrar proveedores y condiciones de pago.
- Registrar facturas, pagos y retenciones.
- Controlar vencimientos y aprobaciones.
- Proyectar necesidades de caja.

## Debe contener
- tablas de proveedores y cuentas por pagar
- reglas de vencimiento y pago
- permisos por rol
- integracion con finanzas y compras
- validaciones de saldo y estado

## Contexto obligatorio
- recibe `usuario`
- debe respetar permisos del portal
- no debe exponer datos fuera del alcance del usuario

## Salida esperada
- estructura de datos
- endpoints o consultas base
- reglas de integracion con el portal principal
