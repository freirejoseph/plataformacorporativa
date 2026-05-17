# AI Configuracion Compartida

Este proyecto usa un `.env` comun para webcode y para VSCode local.

## Modelos activos
- OpenAI: `gpt-4o-mini`
- DeepSeek: `deepseek-chat`
- Gemini: `gemini-2.5-flash`

## Flujo recomendado
1. Abrir el workspace `plataforma.code-workspace`.
2. Cargar la raiz `/home/plataformacorporativa` o `D:\\PROYECTOS\\pPLATAFORMACORPORATIVA`.
3. Leer `.env` desde la raiz del proyecto.
4. Usar el mismo `.env` para extensiones y scripts.

## Nota
No versionar claves reales. Mantener `.env.example` como plantilla segura.
