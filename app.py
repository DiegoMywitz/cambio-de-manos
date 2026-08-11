import html
from datetime import date

import streamlit as st
import pandas as pd

from database import (
    RUBROS, PROVINCIAS, CIUDADES_SUGERIDAS, init_db, crear_publicacion, listar_publicaciones,
    obtener_publicacion, crear_consulta, listar_consultas, marcar_consulta_respondida,
    contar_consultas_por_publicacion,
    listar_publicaciones_de_usuario, activar_publicacion, cambiar_estado_publicacion,
    listar_vendidos_recientes, reporte_precios_por_rubro, listar_top_precios,
    publicacion_duplicada_reciente,
    agregar_imagen, listar_imagenes, imagenes_portada, agregar_video,
    es_favorito, agregar_favorito, quitar_favorito, listar_favoritos_de_usuario,
    crear_alerta, listar_alertas_de_usuario, eliminar_alerta,
)
import style
import auth
import notifications
import payments
import images
import legal
import valuation
import widgets
import georef

VISTA_PARAMS = {
    "publicar": "publicar",
    "franquicias": "franquicias",
    "cotizar": "cotizar",
    "reporte": "ranking",
    "detalle": "negocio",
    "terminos": "terminos",
    "privacidad": "privacidad",
    "mis_publicaciones": "mis-publicaciones",
    "favoritos": "favoritos",
    "alertas": "alertas",
    "acceso": "acceso",
}
PARAM_VISTAS = {param: vista for vista, param in VISTA_PARAMS.items()}

TITULOS_VISTA = {
    "buscar": "Cambio de Manos — Comprá y vendé fondos de comercio en Argentina",
    "publicar": "Publicá tu negocio en venta — Cambio de Manos",
    "franquicias": "Franquicias en venta — Cambio de Manos",
    "cotizar": "Cotizá tu negocio — Cambio de Manos",
    "reporte": "Ranking de precios de negocios — Cambio de Manos",
    "terminos": "Términos y Condiciones — Cambio de Manos",
    "privacidad": "Política de Privacidad — Cambio de Manos",
}

st.set_page_config(page_title="Cambio de Manos",
                    page_icon=str(style.ASSETS_DIR / "favicon.png"), layout="wide",
                    initial_sidebar_state="auto")
style.inject()
if not st.session_state.get("pwa_injected"):
    style.inject_pwa()
    st.session_state.pwa_injected = True
init_db()

if "vista" not in st.session_state:
    _param_inicial = st.query_params.get("p")
    st.session_state.vista = PARAM_VISTAS.get(_param_inicial, "buscar")
    st.session_state.pub_seleccionada = None
    if st.session_state.vista == "detalle":
        _id_inicial = st.query_params.get("id", "")
        if _id_inicial.isdigit():
            st.session_state.pub_seleccionada = int(_id_inicial)
        else:
            st.session_state.vista = "buscar"
    if st.session_state.vista == "publicar":
        # Mercado Pago vuelve acá después del checkout (back_urls en payments.py) — el
        # pago_id en la URL sobrevive aunque la sesión de Streamlit se haya perdido en
        # el ida y vuelta, a diferencia de session_state solo.
        _pago_id_inicial = st.query_params.get("pago_id", "")
        if _pago_id_inicial.isdigit():
            st.session_state.pub_pendiente_pago = int(_pago_id_inicial)
if st.session_state.get("_ultima_vista") != st.session_state.vista:
    style.scroll_to_top()
    st.session_state._ultima_vista = st.session_state.vista
if "pub_seleccionada" not in st.session_state:
    st.session_state.pub_seleccionada = None
if st.session_state.vista != "detalle":
    st.set_page_config(page_title=TITULOS_VISTA.get(st.session_state.vista, "Cambio de Manos"))
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "pub_pendiente_pago" not in st.session_state:
    st.session_state.pub_pendiente_pago = None


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def money(v):
    if v is None:
        return "No especificado"
    return f"${v:,.0f}".replace(",", ".")


def ir_a(vista, pub_id=None):
    st.session_state.vista = vista
    st.session_state.pub_seleccionada = pub_id
    st.query_params.clear()
    param = VISTA_PARAMS.get(vista)
    if param:
        st.query_params["p"] = param
    if vista == "detalle" and pub_id:
        st.query_params["id"] = str(pub_id)


if "verify_token" in st.query_params:
    auth.procesar_verificacion()

if "reset_token" in st.query_params:
    auth.requerir_login()

# ---------- Barra superior ----------
usuario_top = auth.usuario_actual()
barra_izq, barra_der = st.columns([5, 1])
with barra_der:
    if usuario_top:
        nombre_seguro = html.escape(usuario_top["nombre"])
        st.markdown(
            f"<div style='text-align:right; padding-top:0.5rem;'>"
            f"👋 Bienvenido, <b>{nombre_seguro}</b></div>",
            unsafe_allow_html=True,
        )
    else:
        with st.container(key="login_top_btn"):
            st.button("Iniciar sesión", on_click=ir_a, args=("acceso",))

# ---------- Sidebar / navegación ----------
style.sidebar_logo(on_click=ir_a, args=("buscar",))
st.sidebar.caption("Transferencia de fondos de comercio y empresas en Argentina.")
st.sidebar.button("Buscar oportunidades", use_container_width=True,
                   on_click=ir_a, args=("buscar",))
st.sidebar.button("Publicar mi negocio", use_container_width=True,
                   on_click=ir_a, args=("publicar",))
st.sidebar.button("◆ Franquicias", use_container_width=True,
                   on_click=ir_a, args=("franquicias",))
st.sidebar.button("Cotizá tu negocio", use_container_width=True,
                   on_click=ir_a, args=("cotizar",))
st.sidebar.button("Ranking de precios", use_container_width=True,
                   on_click=ir_a, args=("reporte",))

usuario = auth.usuario_actual()
if usuario:
    st.sidebar.button("Mis publicaciones", use_container_width=True,
                       on_click=ir_a, args=("mis_publicaciones",))
    st.sidebar.button("Mis favoritos", use_container_width=True,
                       on_click=ir_a, args=("favoritos",))
    st.sidebar.button("Mis alertas", use_container_width=True,
                       on_click=ir_a, args=("alertas",))

st.sidebar.divider()
st.sidebar.markdown("**Cómo funciona**")
with st.sidebar:
    style.como_funciona()
st.sidebar.divider()

if usuario:
    st.sidebar.caption(f"Sesión iniciada como **{usuario['nombre']}**")
    if notifications.esta_configurado() and not usuario.get("email_verificado"):
        st.sidebar.caption("⚠️ Todavía no confirmaste tu email. Revisá tu bandeja de entrada.")
        if st.sidebar.button("Reenviar email de confirmación", use_container_width=True):
            if auth.reenviar_verificacion(usuario):
                st.sidebar.success("Te reenviamos el email. Revisá también la carpeta de spam.")
            else:
                st.sidebar.error("No pudimos reenviar el email ahora. Probá de nuevo en un rato.")
    st.sidebar.button("Cerrar sesión", use_container_width=True,
                       on_click=lambda: (auth.cerrar_sesion(), ir_a("buscar")))
else:
    st.sidebar.caption("No iniciaste sesión todavía.")

if not notifications.esta_configurado():
    st.sidebar.caption("Notificaciones por email: no configuradas.")
if not images.esta_configurado():
    st.sidebar.caption("Fotos de publicaciones: no configuradas.")
if not payments.esta_configurado():
    st.sidebar.caption("Pagos con Mercado Pago: no configurados.")

st.sidebar.divider()
leg1, leg2 = st.sidebar.columns(2)
leg1.button("Términos", use_container_width=True, on_click=ir_a, args=("terminos",))
leg2.button("Privacidad", use_container_width=True, on_click=ir_a, args=("privacidad",))
st.sidebar.caption("¿Necesitás ayuda? Escribinos a cambiodefirma.contacto@gmail.com")

# ---------- Vista: publicar ----------
if st.session_state.vista == "publicar":
    auth.requerir_login()

    pub_pendiente = st.session_state.get("pub_pendiente_pago")

if st.session_state.vista == "publicar" and not pub_pendiente:
    style.kicker("Alta de publicación")
    st.title("Publicar un negocio en venta")
    st.caption("Cargue los datos básicos de la operación. La información confidencial se comparte "
               "recién cuando avance con un interesado concreto. Los datos de contacto se toman de su cuenta.")

    # Sin st.form: los campos de dinero (widgets.money_input) necesitan reruns en vivo
    # para ir formateando con puntos de miles a medida que se escribe, algo que un
    # st.form no permite (recién dispara on_change al enviar).
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("Título del negocio *", placeholder="Ej: Local de panchos en Palermo", key="pub_titulo")
        rubro = st.selectbox("Rubro *", RUBROS, key="pub_rubro")
        provincia = st.selectbox("Provincia *", PROVINCIAS, key="pub_provincia")
        if st.session_state.get("_pub_provincia_anterior") != provincia:
            st.session_state.pub_localidad_sel = "(elegir o escribir abajo)"
            st.session_state._pub_provincia_anterior = provincia
        localidades_prov = georef.localidades_de_provincia(provincia)
        opciones_localidad = ["(elegir o escribir abajo)"] + localidades_prov + ["Otra (escribir)"]
        localidad_sel = st.selectbox(
            "Localidad / barrio", opciones_localidad,
            help="Empezá a escribir para filtrar las opciones.", key="pub_localidad_sel",
        )
        if localidad_sel == "Otra (escribir)" or not localidades_prov:
            localidad = st.text_input("Escribí la localidad / barrio", key="pub_localidad_otra")
        elif localidad_sel == "(elegir o escribir abajo)":
            localidad = ""
        else:
            localidad = localidad_sel
        antiguedad = st.number_input("Antigüedad (años)", min_value=0, max_value=150, step=1, key="pub_antiguedad")
        empleados = st.number_input("Cantidad de empleados", min_value=0, max_value=10000, step=1, key="pub_empleados")
    with col2:
        precio_venta = widgets.money_input("Precio de venta (ARS) *", key="pub_precio_venta")
        facturacion = widgets.money_input("Facturación mensual promedio (ARS)", key="pub_facturacion")
        resultado = widgets.money_input("Resultado / ganancia mensual (ARS)", key="pub_resultado")
        incluye_inmueble = st.checkbox("Incluye el inmueble en la venta", key="pub_incluye_inmueble")
        motivo_venta = st.text_input("Motivo de la venta", placeholder="Ej: cambio de rubro, jubilación, mudanza",
                                      key="pub_motivo_venta")
        es_franquicia = st.checkbox(
            "◆ Es una oferta de franquicia",
            help="Marcá esto si estás ofreciendo tu marca en franquicia (no la venta de un negocio existente). "
                 "Aparece destacada en la sección 'Franquicias'.",
            key="pub_es_franquicia",
        )

    descripcion = st.text_area("Descripción del negocio *",
                                placeholder="Contá qué vende, por qué es una buena oportunidad, estado del local, equipamiento incluido, etc.",
                                key="pub_descripcion")

    fotos = None
    video = None
    if images.esta_configurado():
        fotos = st.file_uploader(
            "Fotos del negocio (opcional, hasta 5) — sugerimos empezar con una del frente del local",
            type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="pub_fotos",
        )
        if fotos:
            fotos = fotos[:5]
            cols_preview = st.columns(min(len(fotos), 5))
            for col_p, foto_p in zip(cols_preview, fotos):
                col_p.image(foto_p, use_container_width=True)

        video = st.file_uploader(
            "Video corto del negocio (opcional, hasta 60MB)",
            type=["mp4", "mov", "webm"], key="pub_video",
        )
        if video:
            st.video(video)

    tier = "basico"
    if payments.esta_configurado():
        tier_label = st.radio(
            "Nivel de publicación",
            [
                f"Básico — ${payments.PRECIO_PUBLICACION:,.0f} ARS".replace(",", "."),
                f"Destacado — ${payments.PRECIO_DESTACADO:,.0f} ARS (aparece primero en la búsqueda)".replace(",", "."),
            ],
            key="pub_tier_label",
        )
        tier = "destacado" if tier_label.startswith("Destacado") else "basico"
        st.caption("La publicación se activa una vez confirmado el pago.")

    acepto_pub = st.checkbox(
        "Declaro que los datos cargados son reales y acepto los Términos y Condiciones y la Política de Privacidad",
        key="pub_acepto",
    )

    enviado = st.button("Publicar negocio", type="primary", use_container_width=True)

    if enviado:
        faltantes = []
        if not titulo: faltantes.append("Título")
        if not descripcion: faltantes.append("Descripción")
        if not precio_venta: faltantes.append("Precio de venta")
        if not acepto_pub: faltantes.append("Declaración de veracidad y aceptación de Términos y Condiciones")

        if faltantes:
            st.error("Faltan completar: " + ", ".join(faltantes))
        else:
            usuario_id_actual = auth.usuario_actual()["id"]
            pub_existente = publicacion_duplicada_reciente(usuario_id_actual, titulo, precio_venta)
            if pub_existente:
                st.warning("Esta publicación ya se cargó hace un momento (evitamos duplicarla).")
                st.toast("Ya estaba publicada, no se duplicó", icon="ℹ️")
                st.stop()
            estado_inicial = "pendiente_pago" if payments.esta_configurado() else "activa"
            pub_id = crear_publicacion({
                "usuario_id": usuario_id_actual,
                "titulo": titulo,
                "rubro": rubro,
                "provincia": provincia,
                "localidad": localidad,
                "descripcion": descripcion,
                "precio_venta": precio_venta,
                "facturacion_mensual": facturacion or None,
                "resultado_mensual": resultado or None,
                "antiguedad_anios": antiguedad or None,
                "empleados": empleados or None,
                "incluye_inmueble": int(incluye_inmueble),
                "motivo_venta": motivo_venta,
                "es_franquicia": es_franquicia,
            }, estado=estado_inicial, tier=tier)

            # La publicación (pub_id) ya está guardada en este punto — si falla la subida
            # de una foto o el video, no hay que perderla ni tirar un error sin control:
            # se avisa y se sigue, el usuario puede reintentar las fotos/video después.
            fotos_con_error = 0
            fotos_rechazadas = []
            if fotos:
                with st.spinner(f"Subiendo {len(fotos[:5])} foto(s)..."):
                    for i, foto in enumerate(fotos[:5]):
                        contenido_foto = foto.getvalue()
                        apta, motivo_rechazo = images.imagen_es_apta(contenido_foto)
                        if not apta:
                            fotos_rechazadas.append((foto.name, motivo_rechazo))
                            print(f"[publicar] Foto rechazada por moderación en pub {pub_id}: "
                                  f"{foto.name!r} ({motivo_rechazo})")
                            continue
                        try:
                            url = images.subir_imagen(pub_id, contenido_foto, foto.name)
                            agregar_imagen(pub_id, url, orden=i)
                        except Exception as e:
                            fotos_con_error += 1
                            print(f"[publicar] Falló la subida de foto para pub {pub_id}: {e!r}")

            video_con_error = False
            if video:
                with st.spinner("Subiendo video..."):
                    try:
                        video_url = images.subir_video(pub_id, video.getvalue(), video.name)
                        agregar_video(pub_id, video_url)
                    except Exception as e:
                        video_con_error = True
                        print(f"[publicar] Falló la subida de video para pub {pub_id}: {e!r}")

            if fotos_rechazadas:
                st.error(
                    "No se publicaron estas fotos porque no cumplen las normas del sitio: "
                    + ", ".join(f"**{nombre}** ({motivo})" for nombre, motivo in fotos_rechazadas)
                    + ". Si creés que es un error, escribinos a **cambiodefirma.contacto@gmail.com**."
                )

            if fotos_con_error or video_con_error:
                detalle = []
                if fotos_con_error:
                    detalle.append(f"{fotos_con_error} foto(s)")
                if video_con_error:
                    detalle.append("el video")
                st.warning(
                    "La publicación se guardó bien, pero no pudimos subir " + " y ".join(detalle) + ". "
                    "Escribinos a **cambiodefirma.contacto@gmail.com** con el N.º de publicación "
                    f"**{pub_id}** y te ayudamos a agregarlas."
                )

            if estado_inicial == "pendiente_pago":
                st.session_state.pub_pendiente_pago = pub_id
            else:
                st.success(f"Publicación registrada con el identificador N.º {pub_id}.")
                st.toast("¡Publicación enviada!", icon="✅")

            for k in ("pub_titulo", "pub_localidad_otra", "pub_motivo_venta", "pub_descripcion",
                      "_moneyraw_pub_precio_venta", "_moneyraw_pub_facturacion", "_moneyraw_pub_resultado",
                      "pub_antiguedad", "pub_empleados", "pub_incluye_inmueble", "pub_es_franquicia", "pub_acepto"):
                st.session_state.pop(k, None)
            st.rerun()

if st.session_state.vista == "publicar" and pub_pendiente:
        pub_p = obtener_publicacion(pub_pendiente)
        if pub_p and pub_p["estado"] == "pendiente_pago":
            style.kicker("Alta de publicación")
            st.title("Falta confirmar el pago")
            etiqueta_tier = "Destacado" if pub_p["tier"] == "destacado" else "Básico"
            precio_tier = payments.PRECIOS_POR_TIER.get(pub_p["tier"], payments.PRECIO_PUBLICACION)
            st.caption(
                f"Tu publicación **\"{cap(pub_p['titulo'])}\"** quedó guardada como nivel **{etiqueta_tier}** "
                f"(${precio_tier:,.0f} ARS)".replace(",", ".") +
                ", pero no es visible en la búsqueda hasta que se acredite el pago."
            )
            checkout_url = payments.crear_preferencia_publicacion(pub_p["id"], pub_p["titulo"], pub_p["tier"])
            col_pago1, col_pago2 = st.columns(2)
            with col_pago1:
                st.link_button("Pagar publicación", checkout_url, type="primary", use_container_width=True)
            with col_pago2:
                if st.button("Ya pagué, verificar", use_container_width=True):
                    if payments.verificar_pago_aprobado(pub_p["id"]):
                        activar_publicacion(pub_p["id"])
                        st.session_state.pub_pendiente_pago = None
                        st.success("Pago confirmado. Tu publicación ya está activa.")
                        st.rerun()
                    else:
                        st.warning(
                            "Todavía no encontramos el pago acreditado. Puede tardar unos minutos — probá de "
                            "nuevo, o si ya pagaste y no se refleja, mandanos el comprobante a "
                            "**cambiodefirma.contacto@gmail.com** con el N.º de publicación "
                            f"**{pub_p['id']}** y lo activamos manualmente en menos de 48hs."
                        )
            st.divider()
            if st.button("Publicar otro negocio"):
                st.session_state.pub_pendiente_pago = None
                st.query_params.clear()
                st.rerun()

# ---------- Vista: detalle ----------
elif st.session_state.vista == "detalle" and st.session_state.pub_seleccionada:
    pub = obtener_publicacion(st.session_state.pub_seleccionada)
    if pub is None:
        st.warning("Esta publicación ya no existe.")
    else:
        st.set_page_config(page_title=f"{cap(pub['titulo'])} — Cambio de Manos")
        st.button("‹ Volver a la búsqueda", on_click=ir_a, args=("buscar",))
        style.kicker(pub["rubro"])
        if pub.get("es_franquicia"):
            style.badge_franquicia()
        st.title(cap(pub["titulo"]))
        st.caption(f"{pub['rubro']} · {pub['localidad'] or ''} {pub['provincia']}")

        imagenes = listar_imagenes(pub["id"])
        if imagenes:
            cols_img = st.columns(len(imagenes))
            for col_img, img in zip(cols_img, imagenes):
                col_img.image(img["url"], use_container_width=True)

        if pub.get("video_url"):
            st.video(pub["video_url"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Precio de venta", money(pub["precio_venta"]))
        col2.metric("Facturación mensual", money(pub["facturacion_mensual"]))
        col3.metric("Resultado mensual", money(pub["resultado_mensual"]))
        col4.metric("Antigüedad", f"{pub['antiguedad_anios'] or '?'} años")

        st.subheader("Descripción")
        st.write(pub["descripcion"])

        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"**Empleados:** {pub['empleados'] or 'No especificado'}")
            st.markdown(f"**Incluye inmueble:** {'Sí' if pub['incluye_inmueble'] else 'No'}")
        with colB:
            st.markdown(f"**Motivo de venta:** {pub['motivo_venta'] or 'No especificado'}")

        st.divider()

        usuario = auth.usuario_actual()
        es_dueno = usuario and usuario["id"] == pub["usuario_id"]

        if not es_dueno:
            with st.expander("🚩 Reportar esta publicación"):
                with st.form(f"form_reporte_{pub['id']}", clear_on_submit=True):
                    motivo_r = st.selectbox(
                        "Motivo",
                        ["Contenido inapropiado u ofensivo", "Foto o video inapropiado",
                         "Estafa o publicación falsa", "Spam o publicidad no relacionada", "Otro"],
                    )
                    detalle_r = st.text_area("Contanos más (opcional)")
                    enviar_reporte = st.form_submit_button("Enviar reporte")
                    if enviar_reporte:
                        enviado_reporte = notifications.notificar_reporte_publicacion(
                            pub["id"], pub["titulo"], motivo_r, detalle_r,
                            usuario["email"] if usuario else "",
                        )
                        if not enviado_reporte:
                            print(f"[app] Reporte de publicación #{pub['id']} no se pudo enviar por email "
                                  f"(motivo: {motivo_r!r}, detalle: {detalle_r!r})")
                        st.success("Gracias, revisamos la publicación a la brevedad.")

        if usuario and not es_dueno:
            if es_favorito(usuario["id"], pub["id"]):
                if st.button("★ Quitar de favoritos", key=f"fav_detalle_{pub['id']}"):
                    quitar_favorito(usuario["id"], pub["id"])
                    st.rerun()
            else:
                if st.button("☆ Guardar en favoritos", key=f"fav_detalle_{pub['id']}"):
                    agregar_favorito(usuario["id"], pub["id"])
                    st.rerun()

        if es_dueno:
            st.subheader("Consultas recibidas")
            consultas = listar_consultas(pub["id"])
            if not consultas:
                st.info("Todavía no hay consultas para esta publicación.")
            else:
                for c in consultas:
                    st.markdown(f"- **{c['nombre_interesado']}** ({c['email_interesado']}"
                                f"{', ' + c['telefono_interesado'] if c['telefono_interesado'] else ''}) — {c['fecha_creacion']}")
                    if c["mensaje"]:
                        st.caption(c["mensaje"])
                    if c.get("respondida"):
                        st.caption("✅ Marcada como respondida")
                    else:
                        if st.button("Marcar como respondida", key=f"responder_{c['id']}"):
                            marcar_consulta_respondida(c["id"])
                            notificado = notifications.notificar_consulta_respondida(
                                c["email_interesado"], c["nombre_interesado"], pub["titulo"], usuario["nombre"],
                            )
                            if notificado:
                                st.toast("Marcada como respondida. Avisamos al interesado por email.", icon="✅")
                            else:
                                st.toast("Marcada como respondida.", icon="✅")
                            st.rerun()
        else:
            st.subheader("Manifestar interés")
            st.caption("El vendedor recibirá su consulta con sus datos de cuenta y decidirá si avanza.")

            if not usuario:
                st.info("Iniciá sesión o creá una cuenta para dejar una consulta.")
                auth.requerir_login()
            else:
                with st.form("form_consulta", clear_on_submit=True):
                    mensaje_i = st.text_area(
                        "Mensaje (opcional)",
                        placeholder="Contale al vendedor por qué te interesa, tu experiencia, etc.")
                    acepto_consulta = st.checkbox(
                        "Acepto los Términos y Condiciones y la Política de Privacidad "
                        "(mis datos de contacto se compartirán con el vendedor)"
                    )
                    enviar_consulta = st.form_submit_button("Enviar consulta", type="primary")

                    if enviar_consulta and not acepto_consulta:
                        st.error("Tenés que aceptar los Términos y Condiciones para enviar la consulta.")
                    elif enviar_consulta:
                        crear_consulta({
                            "publicacion_id": pub["id"],
                            "usuario_id": usuario["id"],
                            "mensaje": mensaje_i,
                        })
                        notificado = notifications.notificar_nueva_consulta(
                            pub["email_contacto"], pub["titulo"], usuario["nombre"], mensaje_i,
                        )
                        st.toast("¡Tu consulta fue enviada!", icon="✅")
                        if notificado:
                            st.success("Consulta enviada. Avisamos al vendedor por email.")
                        else:
                            st.success("Consulta enviada. El vendedor podrá verla al ingresar a la app.")

# ---------- Vista: mis publicaciones ----------
elif st.session_state.vista == "mis_publicaciones":
    auth.requerir_login()
    usuario = auth.usuario_actual()

    style.kicker("Panel del vendedor")
    st.title("Mis publicaciones")

    propias = listar_publicaciones_de_usuario(usuario["id"])
    if not propias:
        st.info("Todavía no publicaste ningún negocio.")
    else:
        conteo_consultas = contar_consultas_por_publicacion([pub["id"] for pub in propias])
        for pub in propias:
            with st.container(border=True):
                if pub.get("tier") == "destacado":
                    style.badge_destacado()
                if pub.get("es_franquicia"):
                    style.badge_franquicia()
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"### {cap(pub['titulo'])}")
                    estado_legible = "Pendiente de pago" if pub["estado"] == "pendiente_pago" else pub["estado"].capitalize()
                    st.caption(f"{pub['rubro']} · {pub['localidad'] or ''} {pub['provincia']} · Estado: {estado_legible}")
                with c2:
                    st.metric("Precio", money(pub["precio_venta"]))
                with c3:
                    st.metric("Consultas", conteo_consultas.get(pub["id"], 0))

                if pub["estado"] == "pendiente_pago" and payments.esta_configurado():
                    checkout_url = payments.crear_preferencia_publicacion(pub["id"], pub["titulo"], pub["tier"])
                    cp1, cp2 = st.columns(2)
                    with cp1:
                        st.link_button("Pagar publicación", checkout_url, use_container_width=True)
                    with cp2:
                        if st.button("Ya pagué, verificar", key=f"verif_{pub['id']}", use_container_width=True):
                            if payments.verificar_pago_aprobado(pub["id"]):
                                activar_publicacion(pub["id"])
                                st.success("Pago confirmado. Publicación activada.")
                                st.rerun()
                            else:
                                st.warning(
                                    "Todavía no encontramos el pago acreditado. Si ya pagaste y no se refleja, "
                                    "mandanos el comprobante a **cambiodefirma.contacto@gmail.com** con el N.º "
                                    f"de publicación **{pub['id']}** y lo activamos manualmente en menos de 48hs."
                                )
                else:
                    cb1, cb2, cb3 = st.columns(3)
                    with cb1:
                        st.button("Ver", key=f"mis_ver_{pub['id']}",
                                  on_click=ir_a, args=("detalle", pub["id"]),
                                  use_container_width=True)
                    with cb2:
                        if pub["estado"] == "activa":
                            if st.button("Pausar", key=f"pausar_{pub['id']}", use_container_width=True):
                                cambiar_estado_publicacion(pub["id"], "pausada")
                                st.rerun()
                        elif pub["estado"] == "pausada":
                            if st.button("Reactivar", key=f"reactivar_{pub['id']}", use_container_width=True):
                                cambiar_estado_publicacion(pub["id"], "activa")
                                st.rerun()
                    with cb3:
                        if pub["estado"] in ("activa", "pausada"):
                            if st.button("Marcar como vendida", key=f"vendida_{pub['id']}", use_container_width=True):
                                cambiar_estado_publicacion(pub["id"], "vendida")
                                st.rerun()
                        else:
                            if st.button("Reactivar publicación", key=f"revender_{pub['id']}", use_container_width=True):
                                cambiar_estado_publicacion(pub["id"], "activa")
                                st.rerun()

# ---------- Vista: mis favoritos ----------
elif st.session_state.vista == "favoritos":
    auth.requerir_login()
    usuario = auth.usuario_actual()

    style.kicker("Panel del comprador")
    st.title("Mis favoritos")

    guardados = listar_favoritos_de_usuario(usuario["id"])
    if not guardados:
        st.info("Todavía no guardaste ningún negocio. Marcá ☆ Guardar en un negocio que te interese.")
    else:
        portadas = imagenes_portada([pub["id"] for pub in guardados])
        for pub in guardados:
            with st.container(border=True):
                if pub.get("tier") == "destacado":
                    style.badge_destacado()
                if pub.get("es_franquicia"):
                    style.badge_franquicia()
                portada = portadas.get(pub["id"])
                if portada:
                    c0, c1, c2 = st.columns([1, 3, 1])
                    c0.image(portada, use_container_width=True)
                else:
                    c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {cap(pub['titulo'])}")
                    st.caption(f"{pub['rubro']} · {pub['localidad'] or ''} {pub['provincia']}")
                with c2:
                    st.metric("Precio", money(pub["precio_venta"]))
                    st.button("Ver más", key=f"fav_ver_{pub['id']}",
                              on_click=ir_a, args=("detalle", pub["id"]),
                              use_container_width=True)
                    if st.button("★ Quitar", key=f"fav_quitar_{pub['id']}", use_container_width=True):
                        quitar_favorito(usuario["id"], pub["id"])
                        st.rerun()

# ---------- Vista: cotizar ----------
elif st.session_state.vista == "cotizar":
    style.kicker("Herramienta gratuita")
    st.title("Cotizá tu negocio")
    st.caption(
        "Una estimación orientativa según el rubro, para tener un punto de partida antes de fijar "
        "un precio de venta. No reemplaza una tasación profesional (contador o especialista en M&A)."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        rubro_cot = st.selectbox("Rubro", RUBROS, key="rubro_cotizar")
        resultado_cot = widgets.money_input("Ganancia / resultado mensual promedio (ARS)", key="resultado_cotizar")
    with col_b:
        facturacion_cot = widgets.money_input("Facturación mensual promedio (ARS, opcional)", key="facturacion_cotizar")
        antiguedad_cot = st.number_input(
            "Antigüedad (años, opcional)", min_value=0, max_value=150, step=1, key="antiguedad_cotizar",
        )

    if st.button("Calcular estimación", type="primary"):
        resultado = valuation.estimar_valor(rubro_cot, resultado_cot)
        if resultado is None:
            st.warning("Ingresá la ganancia mensual promedio para poder estimar un valor.")
        else:
            valor_min, valor_max, mult_min, mult_max = resultado
            st.divider()
            st.subheader(f"{money(valor_min)} — {money(valor_max)}")
            st.caption(
                f"Cálculo: ganancia anual estimada ({money(resultado_cot * 12)}) × múltiplo típico de "
                f"{rubro_cot} ({mult_min}x a {mult_max}x). Cada rubro tiene un múltiplo distinto porque no "
                "todos los negocios valen lo mismo por cada peso de ganancia: por ejemplo, un negocio de "
                "tecnología con ingresos recurrentes suele valer más múltiplos que un local gastronómico, "
                "que es más volátil y depende más de la ubicación."
            )
            st.info(
                "Esto es solo un punto de partida. El precio final depende de muchos factores que esta "
                "calculadora no ve: ubicación, contrato de alquiler, cartera de clientes, marca, equipamiento, "
                "deudas, y la negociación en sí."
            )
            st.button("Publicar este negocio con estos datos", on_click=ir_a, args=("publicar",))

# ---------- Vista: reporte de precios ----------
elif st.session_state.vista == "reporte":
    style.kicker("Reporte trimestral")
    st.title("Ranking de precios de fondos de comercio en Argentina")
    st.caption(f"Actualizado al {date.today().strftime('%d/%m/%Y')} · Basado en las publicaciones activas y vendidas en Cambio de Manos.")

    st.info(
        "⚠️ Mientras la plataforma crece, esta base incluye publicaciones de ejemplo junto con negocios reales, "
        "así que estos números son solo una referencia orientativa y van a volverse más precisos a medida que "
        "se sumen más operaciones reales."
    )

    st.markdown(
        "¿Cuánto vale un kiosco? ¿Y una peluquería, o una agencia de viajes? Estos son los precios de "
        "publicación promedio por rubro en Cambio de Manos, para tener una primera referencia antes de "
        "vender o comprar un negocio en Argentina."
    )

    filas = reporte_precios_por_rubro()
    if not filas:
        st.warning("Todavía no hay suficientes publicaciones con precio cargado para armar el reporte.")
    else:
        df = pd.DataFrame([
            {
                "Rubro": f["rubro"],
                "Negocios publicados": f["cantidad"],
                "Precio promedio": money(f["precio_promedio"]),
                "Precio mediana": money(f["precio_mediana"]),
            }
            for f in filas
        ])
        st.table(df.set_index("Rubro"))

        st.caption(
            "Metodología: precio promedio y mediana de venta publicados por rubro, sobre publicaciones activas "
            "o vendidas con precio cargado. No incluye datos confidenciales de la negociación final entre las partes."
        )

    st.divider()
    st.subheader("🏆 Ranking: los negocios más caros publicados")
    top = listar_top_precios(limite=10)
    if top:
        for i, t in enumerate(top, start=1):
            st.markdown(f"**{i}. {cap(t['titulo'])}** — {t['rubro']}, {t['provincia']} — {money(t['precio_venta'])}")
    else:
        st.caption("Todavía no hay suficientes datos para armar el ranking.")

    st.divider()
    st.button("Quiero saber cuánto vale mi negocio →", on_click=ir_a, args=("cotizar",), type="primary")

# ---------- Vista: franquicias ----------
elif st.session_state.vista == "franquicias":
    style.kicker("Oportunidades de franquicia")
    st.title("Franquicias disponibles")
    st.caption("Marcas que ofrecen su modelo de negocio en franquicia, en un espacio propio y destacado.")

    franquicias = listar_publicaciones(solo_franquicias=True)
    st.divider()

    if not franquicias:
        st.info(
            "Todavía no hay franquicias publicadas. Si tenés una marca para franquiciar, "
            "marcá la opción 'Es una oferta de franquicia' al publicar tu negocio."
        )
    else:
        st.caption(f"{len(franquicias)} franquicia(s) encontrada(s)")
        portadas = imagenes_portada([pub["id"] for pub in franquicias])
        for pub in franquicias:
            with st.container(border=True):
                style.badge_franquicia()
                if pub.get("tier") == "destacado":
                    style.badge_destacado()
                portada = portadas.get(pub["id"])
                if portada:
                    c0, c1, c2 = st.columns([1, 3, 1])
                    c0.image(portada, use_container_width=True)
                else:
                    c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {cap(pub['titulo'])}")
                    st.caption(f"{pub['rubro']} · {pub['localidad'] or ''} {pub['provincia']}")
                    st.write(pub["descripcion"][:200] + ("..." if len(pub["descripcion"]) > 200 else ""))
                with c2:
                    st.metric("Precio", money(pub["precio_venta"]))
                    st.button("Ver más", key=f"franq_ver_{pub['id']}",
                              on_click=ir_a, args=("detalle", pub["id"]),
                              use_container_width=True)

# ---------- Vista: legales ----------
elif st.session_state.vista == "terminos":
    st.button("‹ Volver", on_click=ir_a, args=("buscar",))
    _leg_col = st.columns([1, 5, 1])[1]
    with _leg_col:
        st.markdown(legal.TERMINOS)
elif st.session_state.vista == "privacidad":
    st.button("‹ Volver", on_click=ir_a, args=("buscar",))
    _leg_col = st.columns([1, 5, 1])[1]
    with _leg_col:
        st.markdown(legal.PRIVACIDAD)

# ---------- Vista: mis alertas ----------
elif st.session_state.vista == "alertas":
    auth.requerir_login()
    usuario = auth.usuario_actual()

    style.kicker("Panel del comprador")
    st.title("Mis alertas de búsqueda")
    st.caption("Te avisamos por email cuando aparezca un negocio nuevo que coincida con estos filtros.")

    alertas = listar_alertas_de_usuario(usuario["id"])
    if not alertas:
        st.info("Todavía no guardaste ninguna alerta. Podés crear una desde 'Buscar oportunidades'.")
    else:
        for alerta in alertas:
            with st.container(border=True):
                precio_txt = money(alerta["precio_max"]) if alerta["precio_max"] else "sin tope"
                st.markdown(
                    f"**Rubro:** {alerta['rubro'] or 'Todos'} · "
                    f"**Provincia:** {alerta['provincia'] or 'Todas'} · "
                    f"**Precio máx.:** {precio_txt}"
                    + (f" · **Palabra clave:** {alerta['texto']}" if alerta["texto"] else "")
                )
                if st.button("Eliminar alerta", key=f"del_alerta_{alerta['id']}"):
                    eliminar_alerta(alerta["id"], usuario["id"])
                    st.rerun()

# ---------- Vista: acceso ----------
elif st.session_state.vista == "acceso":
    if auth.usuario_actual():
        ir_a("buscar")
        st.rerun()
    auth.requerir_login()

# ---------- Vista: buscar (default) ----------
else:
    style.main_logo()
    style.kicker("Oportunidades disponibles")
    st.title("Fondos de comercio y empresas en venta")
    st.caption("Un primer paso para conocer la contraparte, antes de compartir información confidencial.")

    vendidos = listar_vendidos_recientes(limite=6)
    if vendidos:
        items = [f"{cap(v['titulo'])} ({v['provincia']})" for v in vendidos]
        st.success("✅ Vendidos recientemente: " + " · ".join(items))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        rubro_f = st.selectbox("Rubro", ["Todos"] + RUBROS)
    with col2:
        provincia_f = st.selectbox("Provincia", ["Todas"] + PROVINCIAS)
        if st.session_state.get("_provincia_buscar_anterior") != provincia_f:
            st.session_state.localidad_buscar_sel = "Todas"
            st.session_state._provincia_buscar_anterior = provincia_f
    with col3:
        localidades_f = georef.localidades_de_provincia(provincia_f) if provincia_f != "Todas" else []
        localidad_f = st.selectbox("Localidad", ["Todas"] + localidades_f, key="localidad_buscar_sel")
    with col4:
        precio_max_f = widgets.money_input("Precio máximo (ARS)", key="precio_max_buscar")

    def _set_sugerencia(valor):
        st.session_state.texto_busqueda = valor

    texto_f = st.text_input("Buscar por palabra clave", key="texto_busqueda",
                             placeholder="Ej: panchos, kiosco, imprenta...")

    st.caption("Sugerencias rápidas:")
    sug_cols = st.columns(6)
    for col, sugerencia in zip(sug_cols, ["Kiosco", "Panadería", "Restaurante", "Peluquería", "Farmacia", "Ferretería"]):
        with col:
            st.button(sugerencia, key=f"sug_{sugerencia}", use_container_width=True,
                      on_click=_set_sugerencia, args=(sugerencia,))

    if usuario:
        if st.button("🔔 Guardar esta búsqueda como alerta"):
            crear_alerta(
                usuario["id"],
                rubro=rubro_f if rubro_f != "Todos" else None,
                provincia=provincia_f if provincia_f != "Todas" else None,
                precio_max=precio_max_f if precio_max_f > 0 else None,
                texto=texto_f if texto_f else None,
            )
            st.toast("Alerta guardada", icon="🔔")
            st.success("Alerta guardada. Te avisaremos por email cuando aparezcan negocios nuevos que coincidan.")

    publicaciones = listar_publicaciones(
        rubro=rubro_f, provincia=provincia_f, localidad=localidad_f,
        precio_max=precio_max_f if precio_max_f > 0 else None,
        texto=texto_f if texto_f else None,
    )

    st.divider()

    if not publicaciones:
        st.info("Todavía no hay negocios publicados con esos filtros. ¡Sé el primero en publicar uno!")
    else:
        if "resultados_visibles" not in st.session_state:
            st.session_state.resultados_visibles = 20

        st.caption(f"{len(publicaciones)} negocio(s) encontrado(s)")
        visibles = publicaciones[:st.session_state.resultados_visibles]
        portadas = imagenes_portada([pub["id"] for pub in visibles])
        for pub in visibles:
            with st.container(border=True):
                if pub.get("tier") == "destacado":
                    style.badge_destacado()
                if pub.get("es_franquicia"):
                    style.badge_franquicia()

                if usuario:
                    ct1, ct2 = st.columns([10, 1])
                    with ct2:
                        if es_favorito(usuario["id"], pub["id"]):
                            if st.button("★", key=f"fav_{pub['id']}", help="Quitar de favoritos"):
                                quitar_favorito(usuario["id"], pub["id"])
                                st.rerun()
                        else:
                            if st.button("☆", key=f"fav_{pub['id']}", help="Guardar en favoritos"):
                                agregar_favorito(usuario["id"], pub["id"])
                                st.rerun()

                portada = portadas.get(pub["id"])
                if portada:
                    c0, c1, c2 = st.columns([1, 3, 1])
                    c0.image(portada, use_container_width=True)
                else:
                    c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {cap(pub['titulo'])}")
                    st.caption(f"{pub['rubro']} · {pub['localidad'] or ''} {pub['provincia']}")
                    st.write(pub["descripcion"][:200] + ("..." if len(pub["descripcion"]) > 200 else ""))
                with c2:
                    st.metric("Precio", money(pub["precio_venta"]))
                    st.button("Ver más", key=f"ver_{pub['id']}",
                              on_click=ir_a, args=("detalle", pub["id"]),
                              use_container_width=True)

        restantes = len(publicaciones) - len(visibles)
        if restantes > 0:
            if st.button(f"Ver más resultados ({restantes} restantes)", use_container_width=True):
                st.session_state.resultados_visibles += 20
                st.rerun()
