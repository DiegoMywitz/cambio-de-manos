// Worker de Cloudflare para cambiodemanos.com.ar — arregla SEO técnico sin tocar la app.
//
// Qué hace:
//   1. Sirve /robots.txt y /sitemap.xml como archivos reales (Streamlit los intercepta
//      y devuelve el shell de la app en su lugar si no existe este Worker).
//   2. Para el resto de las rutas, deja pasar la respuesta de Render sin tocar, salvo que
//      sea HTML: ahí inyecta <title>/<meta description>/Open Graph según el parámetro
//      `p` de la URL (mismo mapeo que TITULOS_VISTA en app.py — mantenerlos en sync).
//
// Seguridad (no negociable): nunca se toca una respuesta que no sea text/html, ni una
// request con header "Upgrade" (la conexión WebSocket que usa Streamlit para la sesión
// interactiva). Tocar esas rompería la app para usuarios reales, no solo para bots.
//
// Deploy: ver DEPLOY.md en esta misma carpeta.

const SITE = "https://cambiodemanos.com.ar";
const OG_IMAGE = `${SITE}/app/static/icon-512.png`;

const TITULOS = {
  buscar: "Cambio de Manos — Comprá y vendé fondos de comercio en Argentina",
  publicar: "Publicá tu negocio en venta — Cambio de Manos",
  franquicias: "Franquicias en venta — Cambio de Manos",
  cotizar: "Cotizá tu negocio — Cambio de Manos",
  ranking: "Ranking de precios de negocios — Cambio de Manos",
  negocio: "Negocio en venta — Cambio de Manos",
  terminos: "Términos y Condiciones — Cambio de Manos",
  privacidad: "Política de Privacidad — Cambio de Manos",
};

const DESCRIPCIONES = {
  buscar: "Comprá o vendé fondos de comercio y empresas en Argentina. Publicá tu negocio en venta o buscá oportunidades por rubro, provincia y precio.",
  publicar: "Publicá tu negocio en venta en Cambio de Manos, el marketplace de compraventa de fondos de comercio en Argentina.",
  franquicias: "Franquicias en venta en Cambio de Manos: marcas que ofrecen su modelo de negocio en franquicia en toda Argentina.",
  cotizar: "Cotizá el valor estimado de tu negocio según múltiplos de ganancia por rubro, gratis y en minutos.",
  ranking: "Ranking de precios de negocios en venta en Argentina: promedio, mediana y los más caros por rubro.",
  negocio: "Mirá los detalles de este negocio en venta en Cambio de Manos, el marketplace de compraventa de fondos de comercio en Argentina.",
  terminos: "Términos y Condiciones de uso de Cambio de Manos.",
  privacidad: "Política de Privacidad de Cambio de Manos.",
};

const ROBOTS_TXT = `User-agent: *\nAllow: /\n\nSitemap: ${SITE}/sitemap.xml\n`;

// URLs de secciones conocidas. Las fichas individuales de cada negocio no están acá
// todavía (sitemap dinámico queda para más adelante) — Google puede descubrirlas
// igual crawleando los links del listado.
const SITEMAP_PATHS = ["/", "/?p=franquicias", "/?p=ranking", "/?p=cotizar"];

function buildSitemap() {
  const urls = SITEMAP_PATHS.map((path) => `  <url><loc>${SITE}${path}</loc></url>`).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`;
}

function escapeAttr(s) {
  return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

class TitleRewriter {
  constructor(titulo) {
    this.titulo = titulo;
  }
  element(element) {
    element.setInnerContent(this.titulo);
  }
}

class HeadMetaAppender {
  constructor(titulo, descripcion) {
    this.titulo = titulo;
    this.descripcion = descripcion;
  }
  element(element) {
    const titulo = escapeAttr(this.titulo);
    const descripcion = escapeAttr(this.descripcion);
    element.append(
      `<meta name="description" content="${descripcion}">` +
        `<meta property="og:type" content="website">` +
        `<meta property="og:site_name" content="Cambio de Manos">` +
        `<meta property="og:title" content="${titulo}">` +
        `<meta property="og:description" content="${descripcion}">` +
        `<meta property="og:image" content="${OG_IMAGE}">` +
        `<meta name="twitter:card" content="summary_large_image">`,
      { html: true }
    );
  }
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/robots.txt") {
      return new Response(ROBOTS_TXT, { headers: { "content-type": "text/plain; charset=utf-8" } });
    }

    if (request.method === "GET" && url.pathname === "/sitemap.xml") {
      return new Response(buildSitemap(), { headers: { "content-type": "application/xml; charset=utf-8" } });
    }

    const response = await fetch(request);

    // Passthrough total para el WebSocket de Streamlit y para todo lo que no sea HTML
    // (JS, CSS, imágenes, /app/static/*). No leer/tocar el body en esos casos.
    if (request.headers.get("Upgrade") !== null) {
      return response;
    }
    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("text/html")) {
      return response;
    }

    const p = url.searchParams.get("p") || "buscar";
    const titulo = TITULOS[p] || TITULOS.buscar;
    const descripcion = DESCRIPCIONES[p] || DESCRIPCIONES.buscar;

    return new HTMLRewriter()
      .on("title", new TitleRewriter(titulo))
      .on("head", new HeadMetaAppender(titulo, descripcion))
      .transform(response);
  },
};
