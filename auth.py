import re

import streamlit as st

from database import crear_usuario, obtener_usuario_por_email, verificar_password

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def usuario_actual():
    return st.session_state.get("usuario")


def cerrar_sesion():
    st.session_state.usuario = None


def _form_login():
    with st.form("form_login"):
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        enviar = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

        if enviar:
            usuario = obtener_usuario_por_email(email)
            if usuario is None or not verificar_password(usuario, password):
                st.error("Email o contraseña incorrectos.")
            else:
                st.session_state.usuario = dict(usuario)
                st.rerun()


def _form_registro():
    with st.form("form_registro"):
        nombre = st.text_input("Nombre y apellido")
        email = st.text_input("Email")
        telefono = st.text_input("Teléfono (opcional)")
        password = st.text_input("Contraseña", type="password")
        password2 = st.text_input("Repetir contraseña", type="password")
        enviar = st.form_submit_button("Crear cuenta", type="primary", use_container_width=True)

        if enviar:
            if not nombre or not email or not password:
                st.error("Nombre, email y contraseña son obligatorios.")
            elif not EMAIL_RE.match(email):
                st.error("El email no tiene un formato válido.")
            elif len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            elif password != password2:
                st.error("Las contraseñas no coinciden.")
            elif obtener_usuario_por_email(email) is not None:
                st.error("Ya existe una cuenta registrada con ese email.")
            else:
                usuario_id = crear_usuario(nombre, email, password, telefono)
                st.session_state.usuario = dict(obtener_usuario_por_email(email))
                st.success("Cuenta creada correctamente.")
                st.rerun()


def requerir_login():
    """Muestra login/registro y detiene la ejecución hasta que haya sesión iniciada."""
    if usuario_actual():
        return

    import style
    style.kicker("Acceso")
    st.title("Ingresá a tu cuenta")
    st.caption("Necesitás una cuenta para publicar un negocio o dejar una consulta.")

    tab_login, tab_registro = st.tabs(["Ya tengo cuenta", "Crear cuenta"])
    with tab_login:
        _form_login()
    with tab_registro:
        _form_registro()

    st.stop()
