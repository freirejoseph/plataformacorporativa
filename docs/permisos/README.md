# Permisos

## Resolution Order
1. Deny overrides everything.
2. User-specific permission.
3. Group permission.
4. Role permission.
5. Default deny.

## Platform Context
- Every tab receives `usuario`.
- A tab may also receive `rol`, `grupo`, `portal_origen`, and `modulo_origen`.
- Every access should be auditable.

## Rules
- Menus are built from allowed options only.
- Direct access to a tab must still resolve the same permission contract.
- The mother portal owns identity, navigation, and permission administration.
