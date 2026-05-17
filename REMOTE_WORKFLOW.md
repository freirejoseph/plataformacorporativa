# Flujo de trabajo remoto

Este proyecto se desarrolla de forma local en VSCode, pero el código real vive en Ubuntu.

## Objetivo
- Editar desde VSCode local.
- Guardar y ejecutar en `/home/plataformacorporativa` sobre `192.168.1.40`.
- Usar la copia en `D:\PROYECTOS\PLATAFORMACORPORATIVA` solo como respaldo.

## Flujo recomendado
1. Abrir VSCode local.
2. Instalar `Remote - SSH`.
3. Conectarse al host `joseph@192.168.1.40`.
4. Abrir la carpeta `/home/plataformacorporativa`.
5. Programar ahí mismo desde el editor local.
6. Correr pruebas en el terminal remoto.
7. Si hace falta respaldo, sincronizar después con `D:\PROYECTOS\PLATAFORMACORPORATIVA`.

## Qué queda en Ubuntu
- Código fuente real
- `.env`
- servicios
- pruebas
- logs
- datos de desarrollo

## Qué queda en local
- Copia espejo de respaldo
- archivos de apoyo
- documentos de guía

## Nota
No trabajes dos copias activas al mismo tiempo. El servidor Ubuntu es la fuente de verdad.

