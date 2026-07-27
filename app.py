import streamlit as st
import pandas as pd

from database import (
    RUBROS, PROVINCIAS, init_db, crear_publicacion, listar_publicaciones,
    obtener_publicacion, crear_consulta, listar_consultas,
    listar_publicaciones_de_usuario, activar_publicacion,
    agregar_imagen, listar_imagenes, imagenes_portada,
)
import style
import auth
import notifications
import payments
import images

st.set_page_config(page_title="Cambio de Manos",
                    page_icon=str(style.ASSETS_DIR / "favicon.png"), layout="wide")
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


def money(v):
    if v is None:
        return "No especificado"
    return f"${v:,.0f}".replace(",", ".")


def ir_a(vista, pub_id=None):
    st.session_state.vista = vista
    st.session_state.pub_seleccionada = pub_id


# ---------- Sidebar / navegación ----------
style.sidebar_logo()
st.sidebar.caption("Transferencia de fondos de comercio y empresas en Argentina.")
st.sidebar.button("Buscar oportunidades", use_container_width=True,
                   on_click=ir_a, args=("buscar",))
st.sidebar.button("Publicar mi negocio", use_container_width=True,
                   on_click=ir_a, args=("publicar",))

usuario = auth.usuario_actual()
if usuario:
    st.sidebar.button("Mis publicaciones", use_container_width=True,
                       on_click=ir_a, args=("mis_publicaciones",))

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
    st.sidebar.button("Cerrar sesión", use_container_width=True,
                       on_click=lambda: (auth.cerrar_sesion(), ir_a("buscar")))
else:
    st.sidebar.caption("No iniciaste sesión todavía.")

if not notifications.esta_configurado():
    st.sidebar.caption("Notificaciones por email: no configuradas.")
if not images.esta_configurado():
    st.sidebar.caption("Fotos de publicaciones: no configuradas.")

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
            localidad = st.text_input("Localidad / barrio")
            antiguedad = st.number_input("Antigüedad (años)", min_value=0, max_value=150, step=1)
            empleados = st.number_input("Cantidad de empleados", min_value=0, max_value=10000, step=1)
        with col2:
            precio_venta = st.number_input("Precio de venta (ARS) *", min_value=0.0, step=100000.0)
            facturacion = st.number_input("Facturación mensual promedio (ARS)", min_value=0.0, step=50000.0)
            resultado = st.number_input("Resultado / ganancia mensual (ARS)", min_value=0.0, step=50000.0)
            incluye_inmueble = st.checkbox("Incluye el inmueble en la venta")
            motivo_venta = st.text_input("Motivo de la venta", placeholder="Ej: cambio de rubro, jubilación, mudanza")

        descripcion = st.text_area("Descripción del negocio *",
                                    placeholder="Contá qué vende, por qué es una buena oportunidad, estado del local, equipamiento incluido, etc.")

        fotos = None
        if images.esta_configurado():
            fotos = st.file_uploader("Fotos del negocio (opcional, hasta 5)", type=["jpg", "jpeg", "png"],
                                      accept_multiple_files=True)

        if payments.esta_configurado():
            st.caption(f"Costo de publicación: ${payments.PRECIO_PUBLICACION:,.0f} ARS "
                       "(se activa una vez confirmado el pago).".replace(",", "."))

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
                }, estado=estado_inicial)

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
            checkout_url = payments.crear_preferencia_publicacion(pub_p["id"], pub_p["titulo"])
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
        st.title(pub["titulo"])
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
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"### {pub['titulo']}")
                    estado_legible = "Pendiente de pago" if pub["estado"] == "pendiente_pago" else pub["estado"].capitalize()
                    st.caption(f"{pub['rubro']} · {pub['localidad'] or ''} {pub['provincia']} · Estado: {estado_legible}")
                with c2:
                    st.metric("Precio", money(pub["precio_venta"]))
                with c3:
                    n_consultas = len(listar_consultas(pub["id"]))
                    st.metric("Consultas", n_consultas)

                if pub["estado"] == "pendiente_pago" and payments.esta_configurado():
                    checkout_url = payments.crear_preferencia_publicacion(pub["id"], pub["titulo"])
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
                    st.button("Ver", key=f"mis_ver_{pub['id']}",
                              on_click=ir_a, args=("detalle", pub["id"]),
                              use_container_width=True)

# ---------- Vista: buscar (default) ----------
else:
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

    texto_f = st.text_input("Buscar por palabra clave", placeholder="Ej: panchos, kiosco, imprenta...")

    publicaciones = listar_publicaciones(
        rubro=rubro_f, provincia=provincia_f,
        precio_max=precio_max_f if precio_max_f > 0 else None,
        texto=texto_f if texto_f else None,
    )

    st.divider()

    if not publicaciones:
        st.info("Todavía no hay negocios publicados con esos filtros. ¡Sé el primero en publicar uno!")
    else:
        st.caption(f"{len(publicaciones)} negocio(s) encontrado(s)")
        portadas = imagenes_portada([pub["id"] for pub in publicaciones])
        for pub in publicaciones:
            with st.container(border=True):
                portada = portadas.get(pub["id"])
                if portada:
                    c0, c1, c2 = st.columns([1, 3, 1])
                    c0.image(portada, use_container_width=True)
                else:
                    c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {pub['titulo']}")
                    st.caption(f"{pub['rubro']} · {pub['localidad'] or ''} {pub['provincia']}")
                    st.write(pub["descripcion"][:200] + ("..." if len(pub["descripcion"]) > 200 else ""))
                with c2:
                    st.metric("Precio", money(pub["precio_venta"]))
                    st.button("Ver más", key=f"ver_{pub['id']}",
                              on_click=ir_a, args=("detalle", pub["id"]),
                              use_container_width=True)
