# Cambio de Manos — Resumen del proyecto

## Qué es
Marketplace de compra-venta de fondos de comercio y empresas en Argentina (tipo BizBuySell). Publicás un negocio en venta con datos financieros básicos, los compradores buscan y filtran, y dejan una consulta para que el vendedor decida si avanza.

## Estado actual
- **App pública**: https://cambiodemanos.com.ar/ (dominio propio, comprado en NIC Argentina)
- **Hosting**: Render (plan Free) — `cambio-de-manos.onrender.com` es la URL interna de Render, el dominio propio apunta ahí vía Cloudflare (DNS). El plan Free se "duerme" por inactividad, por eso hay un ping automático cada 10 min (ver más abajo).
- **DNS**: delegado a Cloudflare (nameservers `dale.ns.cloudflare.com` / `maxine.ns.cloudflare.com`), registros A de `cambiodemanos.com.ar` y `www.cambiodemanos.com.ar` apuntando a `216.24.57.1` (IP de Render).
- **Streamlit Cloud** (`cambiodemanos.streamlit.app`): hosting anterior, se mantiene prendido de respaldo unos días más y después se borra. **Ya no es la versión activa** — todo el tráfico real va a Render.
- **Acceso directo en el Escritorio**: `Cambio de Manos - App.url` (doble clic abre la app, ya actualizado a cambiodemanos.com.ar)
- **Código fuente**: `C:\Users\Diego Mywitz\Desktop\cambio-de-manos` + backup en GitHub: https://github.com/DiegoMywitz/cambio-de-manos (repo público, auto-deploy a Render en cada push a `master`)
- **Base de datos**: Postgres en Supabase (proyecto "cambio de manos", ref `jzncffmulogpyozyhccs`), compartida por todos los hostings — nunca se pierde aunque se reinicie o borre un deploy.
- Tiene negocios de ejemplo cargados en las 24 provincias/jurisdicciones, más algunos de franquicia, para probar/mostrar.

## Funcionalidades ya construidas
- Registro/login de usuarios (contraseñas hasheadas), con checkbox de aceptación de Términos y Condiciones en registro, al publicar, y al dejar una consulta
- Publicar negocio: título, rubro, provincia, **localidad completada según la provincia con el listado oficial completo de Argentina** (API pública Georef del Ministerio del Interior, `georef.py`), precio, facturación, ganancia, antigüedad, empleados, motivo de venta, hasta 5 fotos, checkbox de franquicia
- Los campos de dinero (precio, facturación, ganancia) se formatean con puntos de miles mientras se escribe (`widgets.py`, `money_input`)
- Búsqueda con filtros: rubro, provincia, **localidad** (dependiente de la provincia, mismo dato de Georef), precio máximo, texto libre + sugerencias rápidas de rubros comunes
- Franja de "Vendidos recientemente" y sección "Ranking de precios" (promedio/mediana por rubro + top 10 más caros) como contenido de SEO — accesible sin login
- Calculadora "Cotizá tu negocio": estima un rango de valor según múltiplos de ganancia anual distintos por rubro (`valuation.py`)
- Sección "Franquicias" propia, con badge distintivo (◆), separada de la venta de negocios
- Paginación de resultados (20 por vez, botón "Ver más")
- Ficha de detalle de cada negocio + formulario de consulta para interesados
- "Mis publicaciones": panel del vendedor con consultas recibidas, botón "Marcar como respondida" (avisa por email al interesado)
- "Mis favoritos" (☆/★ Guardar) y "Mis alertas" de búsqueda por email
- Estados de publicación: activa / pausada / vendida (con fecha de venta para el ranking de "vendidos recientemente")
- Notificaciones por email: nueva consulta, consulta respondida, alerta de búsqueda, recuperar contraseña, verificar email (cuenta `cambiodefirma.contacto@gmail.com`)
- **Pagos con Mercado Pago activados**: niveles Básico ($9.999)/Destacado ($19.999) por publicación, con Access Token de prueba cargado. El nombre público en el checkout es "Cambiodemanos" (configurado en el perfil de Mercado Pago para no mostrar el nombre personal del dueño)
- PWA instalable: manifest + íconos servidos como estáticos, se puede "Agregar a pantalla de inicio" en Android/iOS
- Diseño: logo propio (SVG), paleta navy + azul + dorado, tema forzado a claro (`primaryColor` propio, no el rojo por defecto de Streamlit), sidebar automático (expandido en escritorio, colapsado en celular)
- Legales: página de Términos y Condiciones (con cláusula de indemnidad) y Política de Privacidad (`legal.py`)

## Automatizaciones (Task Scheduler de Windows, dependen de que la PC de Diego esté prendida)
- `CambioDeManos_AlertasBusqueda`: corre `alertas_job.py` 1 vez al día, manda los emails de alertas de búsqueda guardadas
- `CambioDeManos_PingKeepAlive`: corre `ping_app.py` cada 10 min, le pega a `https://cambiodemanos.com.ar/` para que Render no la duerma por inactividad

## Pendiente / para retomar
1. **Pasar Mercado Pago a producción**: hoy está con credenciales de **prueba** (`APP_USR-...` de la pestaña "Credenciales de prueba"). Para cobrar de verdad hay que ir a Credenciales de producción y reemplazar `CDM_MP_ACCESS_TOKEN` en Render.
2. **Revisión legal real**: los Términos/Privacidad son un borrador razonable, no reemplazan a un abogado — importante antes de escalar con cobros reales.
3. **Marketing/SEO de contenido**: ideas pendientes — reporte de precios ya armado; falta domain authority (backlinks), alta en Google Search Console, y evaluar agregar datos de fuentes externas (diarios, Mercado Libre) para enriquecer el ranking — proyecto aparte, cuidado con términos de uso de terceros si se scrapea.
4. **Privacidad del titular del dominio**: `.com.ar` no tiene protección de privacidad en NIC Argentina — el nombre real de Diego es públicamente consultable vía Whois. Se resolvería registrando a nombre de una empresa constituida, no antes.
5. **Borrar Streamlit Cloud** una vez confirmado que todo funciona bien en Render + dominio propio hace un tiempo prudencial.
6. Se probó y sacó un mapa de provincias (daba problemas de carga en producción) — descartado por ahora, no reintentar sin resolver antes por qué se colgaba.
7. App móvil nativa (Android/iOS en las tiendas): evaluar recién cuando el negocio esté validado — implica reescritura o Capacitor, cuenta de Google Play (u$s25 único pago) y Apple Developer (u$s99/año) con revisión de Apple.

## Datos de acceso importantes
- **Cuenta de email de notificaciones**: `cambiodefirma.contacto@gmail.com` (contraseña de aplicación configurada como secret)
- **Cuenta de Supabase**: asociada a la cuenta de Google del usuario (`diegomywitz@gmail.com`)
- **GitHub**: repo bajo `DiegoMywitz/cambio-de-manos`; el navegador del usuario está logueado como `diegomywitz-arch` (cuenta distinta a la de la terminal `DiegoMywitz` — diegomywitz-arch quedó como colaborador admin del repo)
- **Render**: cuenta creada con GitHub (`diegomywitz-arch`), workspace "My Workspace". El repo se conectó como "Public Git Repository" (no requiere reinstalar el GitHub App), y el auto-deploy sí funciona con ese método.
- **Streamlit Cloud** (hosting viejo, de respaldo): el deploy real vive en el **workspace `diegomywitz`** (con cuenta `diegomywitz@gmail.com`), NO en `diegomywitz-arch` — ese workspace aparece vacío y confunde.
- **NIC Argentina** (dominio): cuenta con Clave Fiscal de AFIP de Diego (CUIT terminado en `1997`), nivel 2. Dominio `cambiodemanos.com.ar` registrado 31/07/2026, vence 31/07/2027 (renovación anual, ~$8.500 ARS/año).
- **Cloudflare** (DNS): cuenta creada con `diegomywitz@gmail.com`, plan Free.
- **Mercado Pago**: cuenta personal de Diego, aplicación "Cambio de Manos" tipo Checkout Pro. Nombre público configurado como "Cambiodemanos" en el perfil, para no exponer el nombre personal a los compradores.
- Todas las credenciales (DB, SMTP, Supabase Storage, Mercado Pago) están en `.streamlit/secrets.toml` local (no se sube a git) y replicadas como Environment Variables en Render (y en los Secrets de Streamlit Cloud, aunque ya no es la versión activa).
