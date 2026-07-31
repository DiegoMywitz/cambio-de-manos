import html

import streamlit as st
import pandas as pd

from database import (
    RUBROS, PROVINCIAS, CIUDADES_SUGERIDAS, init_db, crear_publicacion, listar_publicaciones,
    obtener_publicacion, crear_consulta, listar_consultas, marcar_consulta_respondida,
    listar_publicaciones_de_usuario, activar_publicacion, cambiar_estado_publicacion,
    agregar_imagen, listar_imagenes, imagenes_portada,
    es_favorito, agregar_favorito, quitar_favorito, listar_favoritos_de_usuario,
    crear_alerta, listar_alertas_de_usuario, eliminar_alerta,
)
import style
import auth
import notifications
import payments
import images
import legal

st.set_page_config(page_title="Cambio de Manos",
                    page_icon=str(style.ASSETS_DIR / "favicon.png"), layout="wide",
                    initial_sidebar_state="expanded")
style.inject()
init_db()

if "vista" not in st.session_state:
    st.session_state.vista = "buscar"
if "pub_seleccionada" not in st.session_state:
    st.session_state.pub_seleccionada = None
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
        st.markdown(
            "<div style='text-align:right; padding-top:0.5rem;'>No iniciaste sesión</div>",
            unsafe_allow_html=True,
        )

# ---------- Sidebar / navegación ----------
style.sidebar_logo()
st.sidebar.caption("Transferencia de fondos de comercio y empresas en Argentina.")
st.sidebar.button("Buscar oportunidades", use_container_width=True,
                   on_click=ir_a, args=("buscar",))
st.sidebar.button("Publicar mi negocio", use_container_width=True,
                   on_click=ir_a, args=("publicar",))
st.sidebar.button("◆ Franquicias", use_container_width=True,
                   on_click=ir_a, args=("franquicias",))

usuario = auth.usuario_actual()
if usuario:
    st.sidebar.button("Mis publicaciones", use_container_width=True,
                       on_click=ir_a, args=("mis_publicaciones",))
    st.sidebar.button("Mis favoritos", use_container_width=True,
                       on_click=ir_a, args=("favoritos",))
    st.sidebar.button("Mis alertas", use_container_width=True,
                       on_click=ir_a, args=("alertas",))

st.sidebar.divider()
st.sidebar.markdown(
    "**Cómo funciona**\n\n"
    "1. El vendedor publica datos básicos del negocio, sin exponer información confidencial.\n"
    "2. El comprador filtra por rubro, ubicación y presupuesto.\n"
    "3. Si hay interés, deja sus datos y el vendedor evalúa si avanza.\n"
    "4. El contacto directo y la negociación quedan entre las partes."
)
st.sidebar.divider()

if usuario:
    st.sidebar.caption(f"Sesión iniciada como **{usuario['nombre']}**")
    if notifications.esta_configurado() and not usuario.get("email_verificado"):
        st.sidebar.caption("⚠️ Todavía no confirmaste tu email. Revisá tu bandeja de entrada.")
    st.sidebar.button("Cerrar sesión", use_container_width=True,
                       on_click=lambda: (auth.cerrar_sesion(), ir_a("buscar")))
else:
    st.sidebar.caption("No iniciaste sesión todavía.")

if not notifications.esta_configurado():
    st.sidebar.caption("Notificaciones por email: no configuradas.")
if not images.esta_configurado():
    st.sidebar.caption("Fotos de publicaciones: no configuradas.")

st.sidebar.divider()
leg1, leg2 = st.sidebar.columns(2)
leg1.button("Términos", use_container_width=True, on_click=ir_a, args=("terminos",))
leg2.button("Privacidad", use_container_width=True, on_click=ir_a, args=("privacidad",))

# ---------- Vista: publicar ----------
if st.session_state.vista == "publicar":
    auth.requerir_login()

    style.kicker("Alta de publicación")
    st.title("Publicar un negocio en venta")
    st.caption("Cargue los datos básicos de la operación. La información confidencial se comparte "
               "recién cuando avance con un interesado concreto. Los datos de contacto se toman de su cuenta.")

    with st.form("form_publicar", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("Título del negocio *", placeholder="Ej: Local de panchos en Palermo")
            rubro = st.selectbox("Rubro *", RUBROS)
            provincia = st.selectbox("Provincia *", PROVINCIAS)
            localidad_sel = st.selectbox(
                "Localidad / barrio", ["(elegir o escribir abajo)"] + CIUDADES_SUGERIDAS + ["Otra (escribir)"],
                help="Empezá a escribir para filtrar las opciones.",
            )
            if localidad_sel == "Otra (escribir)":
                localidad = st.text_input("Escribí la localidad / barrio")
            elif localidad_sel == "(elegir o escribir abajo)":
                localidad = ""
            else:
                localidad = localidad_sel
            antiguedad = st.number_input("Antigüedad (años)", min_value=0, max_value=150, step=1)
            empleados = st.number_input("Cantidad de empleados", min_value=0, max_value=10000, step=1)
        with col2:
            precio_venta = st.number_input("Precio de venta (ARS) *", min_value=0.0, step=100000.0)
            facturacion = st.number_input("Facturación mensual promedio (ARS)", min_value=0.0, step=50000.0)
            resultado = st.number_input("Resultado / ganancia mensual (ARS)", min_value=0.0, step=50000.0)
            incluye_inmueble = st.checkbox("Incluye el inmueble en la venta")
            motivo_venta = st.text_input("Motivo de la venta", placeholder="Ej: cambio de rubro, jubilación, mudanza")
            es_franquicia = st.checkbox(
                "◆ Es una oferta de franquicia",
                help="Marcá esto si estás ofreciendo tu marca en franquicia (no la venta de un negocio existente). "
                     "Aparece destacada en la sección 'Franquicias'.",
            )

        descripcion = st.text_area("Descripción del negocio *",
                                    placeholder="Contá qué vende, por qué es una buena oportunidad, estado del local, equipamiento incluido, etc.")

        fotos = None
        if images.esta_configurado():
            fotos = st.file_uploader("Fotos del negocio (opcional, hasta 5)", type=["jpg", "jpeg", "png"],
                                      accept_multiple_files=True)

        tier = "basico"
        if payments.esta_configurado():
            tier_label = st.radio(
                "Nivel de publicación",
                [
                    f"Básico — ${payments.PRECIO_PUBLICACION:,.0f} ARS".replace(",", "."),
                    f"Destacado — ${payments.PRECIO_DESTACADO:,.0f} ARS (aparece primero en la búsqueda)".replace(",", "."),
                ],
            )
            tier = "destacado" if tier_label.startswith("Destacado") else "basico"
            st.caption("La publicación se activa una vez confirmado el pago.")

        enviado = st.form_submit_button("Publicar negocio", type="primary", use_container_width=True)

        if enviado:
            faltantes = []
            if not titulo: faltantes.append("Título")
            if not descripcion: faltantes.append("Descripción")
            if not precio_venta: faltantes.append("Precio de venta")

            if faltantes:
                st.error("Faltan completar: " + ", ".join(faltantes))
            else:
                estado_inicial = "pendiente_pago" if payments.esta_configurado() else "activa"
                pub_id = crear_publicacion({
                    "usuario_id": auth.usuario_actual()["id"],
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

                if fotos:
                    for i, foto in enumerate(fotos[:5]):
                        url = images.subir_imagen(pub_id, foto.getvalue(), foto.name)
                        agregar_imagen(pub_id, url, orden=i)

                if estado_inicial == "pendiente_pago":
                    st.session_state.pub_pendiente_pago = pub_id
                else:
                    st.success(f"Publicación registrada con el identificador N.º {pub_id}.")

    pub_pendiente = st.session_state.get("pub_pendiente_pago")
    if pub_pendiente:
        pub_p = obtener_publicacion(pub_pendiente)
        if pub_p and pub_p["estado"] == "pendiente_pago":
            st.divider()
            st.subheader("Falta confirmar el pago")
            st.caption("Tu publicación quedó guardada, pero no es visible en la búsqueda hasta que se acredite el pago.")
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
                        st.warning("Todavía no encontramos el pago acreditado. Probá de nuevo en unos minutos.")

# ---------- Vista: detalle ----------
elif st.session_state.vista == "detalle" and st.session_state.pub_seleccionada:
    pub = obtener_publicacion(st.session_state.pub_seleccionada)
    if pub is None:
        st.warning("Esta publicación ya no existe.")
    else:
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
                                st.success("Marcada como respondida. Avisamos al interesado por email.")
                            else:
                                st.success("Marcada como respondida.")
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
                    enviar_consulta = st.form_submit_button("Enviar consulta", type="primary")

                    if enviar_consulta:
                        crear_consulta({
                            "publicacion_id": pub["id"],
                            "usuario_id": usuario["id"],
                            "mensaje": mensaje_i,
                        })
                        notificado = notifications.notificar_nueva_consulta(
                            pub["email_contacto"], pub["titulo"], usuario["nombre"], mensaje_i,
                        )
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
                    n_consultas = len(listar_consultas(pub["id"]))
                    st.metric("Consultas", n_consultas)

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
                                st.warning("Todavía no encontramos el pago acreditado.")
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
    st.markdown(legal.TERMINOS)
elif st.session_state.vista == "privacidad":
    st.button("‹ Volver", on_click=ir_a, args=("buscar",))
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

# ---------- Vista: buscar (default) ----------
else:
    style.main_logo()
    style.kicker("Oportunidades disponibles")
    st.title("Fondos de comercio y empresas en venta")
    st.caption("Un primer paso para conocer la contraparte, antes de compartir información confidencial.")

    col1, col2, col3 = st.columns(3)
    with col1:
        rubro_f = st.selectbox("Rubro", ["Todos"] + RUBROS)
    with col2:
        provincia_f = st.selectbox("Provincia", ["Todas"] + PROVINCIAS)
    with col3:
        precio_max_f = st.number_input("Precio máximo (ARS)", min_value=0.0, step=500000.0, value=0.0)

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
            st.success("Alerta guardada. Te avisaremos por email cuando aparezcan negocios nuevos que coincidan.")

    publicaciones = listar_publicaciones(
        rubro=rubro_f, provincia=provincia_f,
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
