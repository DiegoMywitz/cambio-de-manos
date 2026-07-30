# Cambio de Manos — Resumen del proyecto

## Qué es
Marketplace de compra-venta de fondos de comercio y empresas en Argentina (tipo BizBuySell). Publicás un negocio en venta con datos financieros básicos, los compradores buscan y filtran, y dejan una consulta para que el vendedor decida si avanza.

## Estado actual
- **App pública**: https://cambiodemanos.streamlit.app/
- **Acceso directo en el Escritorio**: `Cambio de Manos - App.url` (doble clic abre la app)
- **Código fuente**: `C:\Users\Diego Mywitz\Desktop\cambio-de-manos` + backup en GitHub: https://github.com/DiegoMywitz/cambio-de-manos (repo público)
- **Base de datos**: Postgres en Supabase (proyecto "cambio de manos", ref `jzncffmulogpyozyhccs`), completamente separada de Streamlit — nunca se pierde aunque se reinicie o borre el deploy.
- Actualmente tiene ~168 negocios de ejemplo cargados en las 24 provincias, para probar/mostrar.

## Funcionalidades ya construidas
- Registro/login de usuarios (contraseñas hasheadas)
- Publicar negocio: título, rubro, provincia/localidad (con autocompletado de ciudades), precio, facturación, ganancia, antigüedad, empleados, motivo de venta, hasta 5 fotos
- Búsqueda con filtros (rubro, provincia, precio) + sugerencias rápidas de rubros comunes
- Paginación de resultados (20 por vez, botón "Ver más")
- Ficha de detalle de cada negocio + formulario de consulta para interesados
- "Mis publicaciones": panel del vendedor con consultas recibidas
- Notificaciones por email al vendedor cuando llega una consulta (cuenta `cambiodefirma.contacto@gmail.com`)
- Pagos con Mercado Pago: niveles Básico/Destacado por publicación (código listo, **falta activar con credenciales reales de Mercado Pago** — quedó pendiente, no se completó la cuenta/token)
- Diseño: logo propio (SVG), paleta navy + azul + dorado, sidebar fijo (no colapsable) con logo y navegación

## Pendiente / para retomar
1. **Mercado Pago**: crear cuenta y sacar Access Token (de prueba o producción) en mercadopago.com.ar/developers/panel, agregarlo como secret `CDM_MP_ACCESS_TOKEN` en Streamlit Cloud (Manage app → Settings → Secrets).
2. **Nombre de URL más corto / dominio propio**: quedó en `cambiodemanos.streamlit.app`, se puede evaluar comprar un dominio propio más adelante.
3. **Marketing**: hay un análisis de BizBuySell (competidor de EE.UU.) hecho en esta conversación con ideas concretas — contenido/SEO tipo "reporte de precios trimestral", mensaje de marca contra quejas típicas del rubro (sin renovación automática sorpresa, sin bots, respuesta humana), niveles de publicación pagos.
4. Se probó y sacó un mapa de provincias (daba problemas de carga en producción) — descartado por ahora, no reintentar sin resolver antes por qué se colgaba.
5. Quedó sin resolver del todo por qué el sidebar no aparecía en algunas verificaciones automatizadas contra la versión pública — funcionaba perfecto en local; si el usuario confirma que en su navegador se ve bien, no hace falta tocar nada más.

## Datos de acceso importantes
- **Cuenta de email de notificaciones**: `cambiodefirma.contacto@gmail.com` (contraseña de aplicación configurada como secret)
- **Cuenta de Supabase**: asociada a la cuenta de GitHub/Google del usuario
- **GitHub**: repo bajo `DiegoMywitz/cambio-de-manos`; el navegador del usuario está logueado como `diegomywitz-arch` (cuenta distinta a la de la terminal `DiegoMywitz` — diegomywitz-arch quedó como colaborador admin del repo)
- Todas las credenciales (DB, SMTP, Supabase Storage) están en `.streamlit/secrets.toml` local (no se sube a git) y replicadas en los Secrets de Streamlit Cloud.
