# Deployar el Worker de SEO (paso a paso)

Esto lo tenés que hacer vos porque necesita tu login de Cloudflare — no tengo esas credenciales.
Es la misma cuenta que ya usás para el DNS del dominio (`diegomywitz@gmail.com`).

## 1. Crear el Worker

1. Entrá a [dash.cloudflare.com](https://dash.cloudflare.com) con esa cuenta.
2. En el menú de la izquierda: **Workers y Pages** → **Create** (o "Crear aplicación") → **Create Worker**.
3. Ponele un nombre, por ejemplo `cambio-de-manos-seo`. Click en **Deploy** para crear la versión vacía inicial.
4. Click en **Edit code** (o "Editar código").
5. Borrá todo el código de ejemplo que trae por defecto, y pegá el contenido completo del archivo [`seo-worker.js`](seo-worker.js) de esta carpeta.
6. Click en **Deploy** (o **Save and Deploy**) arriba a la derecha.

## 2. Conectarlo al dominio

Esto es lo que hace que el Worker realmente intercepte el tráfico de `cambiodemanos.com.ar` (si te salteás este paso, el Worker existe pero no hace nada).

1. Dentro del Worker que acabás de crear, andá a la pestaña **Settings** → **Domains & Routes** (o **Triggers** → **Routes**, el nombre varía un poco según la versión del dashboard).
2. **Add** → **Route** (no "Custom Domain" — Route es lo correcto acá porque el dominio ya apunta a Render, no queremos que Cloudflare lo sirva directo).
3. Route: `cambiodemanos.com.ar/*`. Zone: `cambiodemanos.com.ar`. Guardar.
4. Repetí para `www.cambiodemanos.com.ar/*` si ese subdominio también está en uso.

## 3. Probar que funciona

Una vez guardado (puede tardar uno o dos minutos en propagar), probá desde una terminal o pedime a mí que lo revise:

- `https://cambiodemanos.com.ar/robots.txt` → tiene que mostrar texto plano (`User-agent: *` ...), no la app.
- `https://cambiodemanos.com.ar/sitemap.xml` → tiene que mostrar XML.
- Entrá normal a `https://cambiodemanos.com.ar/` y navegá un poco (buscar, publicar, franquicias) — la app tiene que funcionar exactamente igual que antes. Si algo se rompe (la app no carga, tira error), avisame y lo revisamos — puede ser el filtro de content-type/Upgrade del Worker, no debería pasar pero es lo primero que miraría.

## 4. Alta en Google Search Console

1. Andá a [search.google.com/search-console](https://search.google.com/search-console).
2. **Agregar propiedad** → elegí el tipo **Dominio** (no "Prefijo de URL") → poné `cambiodemanos.com.ar`.
3. Google te va a dar un registro **TXT** para verificar que sos el dueño del dominio.
4. Andá a Cloudflare → tu dominio → **DNS** → **Records** → **Add record**: Type `TXT`, Name `@`, Content: el valor exacto que te dio Google. Guardar.
5. Volvé a Search Console y hacé click en **Verificar**.
6. Ya verificado: en el menú lateral, **Sitemaps** → pegá `sitemap.xml` → **Enviar**.

## 5. Chequear si Google puede ver el contenido real (el paso que decide si hace falta la Fase 2)

1. En Search Console, arriba hay una barra de **Inspección de URLs**. Pegá `https://cambiodemanos.com.ar/?p=franquicias` (o cualquier URL de una ficha, tipo `.../?p=negocio&id=169`) y Enter.
2. Click en **Probar URL publicada** (Live Test).
3. Cuando termine, click en **Ver la página probada** → pestaña **HTML** (o la captura de pantalla).
4. Ahí es donde importa mirar bien: no alcanza con que diga "la URL se puede indexar" — hay que buscar en ese HTML si aparece el *contenido real* (el nombre del negocio, el precio, la descripción), no solo el título/description que ya inyecta el Worker.
   - Si aparece el contenido real → con esto alcanza, no hace falta nada más.
   - Si el HTML capturado está vacío o casi vacío (solo el título/description) → avisame con una captura, esa es la señal para pasar a la Fase 2 (que ya está pensada y documentada, pendiente de decidir si se justifica).

Cualquier duda en el medio, mandame captura de pantalla de lo que ves y seguimos desde ahí.
