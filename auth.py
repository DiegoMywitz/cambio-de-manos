import re

import streamlit as st

from database import (
    crear_usuario, obtener_usuario_por_email, verificar_password,
    crear_token_reset, obtener_reset_valido, actualizar_password_con_token,
    crear_token_verificacion, verificar_email_con_token,
)
import notifications
import legal

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
APP_URL = "https://cambiodemanos.streamlit.app/"


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


def _form_olvide_password():
    with st.form("form_olvide_password"):
        email = st.text_input("Email de tu cuenta")
        enviar = st.form_submit_button("Enviar link de recuperación", use_container_width=True)

        if enviar:
            usuario = obtener_usuario_por_email(email)
            if usuario is not None:
                token = crear_token_reset(usuario["id"])
                link = f"{APP_URL}?reset_token={token}"
                if notifications.esta_configurado():
                    notifications.notificar_reset_password(usuario["email"], usuario["nombre"], link)
                else:
                    st.info(f"Notificaciones por email no configuradas. Link de prueba: {link}")
            # Mismo mensaje exista o no la cuenta, para no revelar qué emails están registrados.
            st.success(
                "Si el email está registrado, te enviamos un link para elegir una nueva contraseña. "
                "Revisá tu bandeja de entrada (y spam)."
            )


def _form_nueva_password(token: str):
    reset = obtener_reset_valido(token)
    import style
    style.kicker("Recuperar contraseña")
    st.title("Elegí una nueva contraseña")

    if reset is None:
        st.error("Este link ya fue usado o venció. Pedí uno nuevo desde 'Ya tengo cuenta'.")
        if st.button("Volver al ingreso"):
            st.query_params.clear()
            st.rerun()
        st.stop()

    if st.session_state.get("password_reset_ok"):
        st.success("Contraseña actualizada. Ya podés ingresar con tu nueva contraseña.")
        if st.button("Ir a ingresar"):
            st.session_state.password_reset_ok = False
            st.query_params.clear()
            st.rerun()
        st.stop()

    st.caption(f"Cuenta: {reset['email']}")
    with st.form("form_nueva_password"):
        password = st.text_input("Nueva contraseña", type="password")
        password2 = st.text_input("Repetir nueva contraseña", type="password")
        enviar = st.form_submit_button("Guardar nueva contraseña", type="primary", use_container_width=True)

        if enviar:
            if len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            elif password != password2:
                st.error("Las contraseñas no coinciden.")
            else:
                actualizar_password_con_token(token, password)
                st.session_state.usuario = None
                st.session_state.password_reset_ok = True
                st.rerun()
    st.stop()


def _form_registro():
    with st.expander("Leer Términos y Condiciones y Política de Privacidad"):
        st.markdown(legal.TERMINOS)
        st.divider()
        st.markdown(legal.PRIVACIDAD)

    with st.form("form_registro"):
        nombre = st.text_input("Nombre y apellido")
        email = st.text_input("Email")
        telefono = st.text_input("Teléfono (opcional)")
        password = st.text_input("Contraseña", type="password")
        password2 = st.text_input("Repetir contraseña", type="password")
        acepto = st.checkbox("Leí y acepto los Términos y Condiciones y la Política de Privacidad")
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
            elif not acepto:
                st.error("Tenés que aceptar los Términos y Condiciones y la Política de Privacidad para crear la cuenta.")
            elif obtener_usuario_por_email(email) is not None:
                st.error("Ya existe una cuenta registrada con ese email.")
            else:
                usuario_id = crear_usuario(nombre, email, password, telefono)
                st.session_state.usuario = dict(obtener_usuario_por_email(email))
                if notifications.esta_configurado():
                    token = crear_token_verificacion(usuario_id)
                    link = f"{APP_URL}?verify_token={token}"
                    notifications.notificar_verificacion_email(email, nombre, link)
                    st.success("Cuenta creada correctamente. Te enviamos un email para confirmar tu dirección.")
                else:
                    st.success("Cuenta creada correctamente.")
                st.rerun()


def procesar_verificacion():
    verify_token = st.query_params.get("verify_token")
    if not verify_token:
        return
    ok = verificar_email_con_token(verify_token)
    st.query_params.clear()
    if ok:
        st.toast("Email verificado correctamente.", icon="✅")
        if usuario_actual() and usuario_actual()["id"]:
            usuario_refrescado = obtener_usuario_por_email(usuario_actual()["email"])
            if usuario_refrescado:
                st.session_state.usuario = dict(usuario_refrescado)
    else:
        st.toast("Ese link de verificación ya fue usado o venció.", icon="⚠️")


def requerir_login():
    """Muestra login/registro y detiene la ejecución hasta que haya sesión iniciada."""
    if "verify_token" in st.query_params:
        procesar_verificacion()

    token = st.query_params.get("reset_token")
    if token:
        _form_nueva_password(token)
        return

    if usuario_actual():
        return

    import style
    style.kicker("Acceso")
    st.title("Ingresá a tu cuenta")
    st.caption("Necesitás una cuenta para publicar un negocio o dejar una consulta.")

    tab_login, tab_registro = st.tabs(["Ya tengo cuenta", "Crear cuenta"])
    with tab_login:
        _form_login()
        with st.expander("¿Olvidaste tu contraseña?"):
            _form_olvide_password()
    with tab_registro:
        _form_registro()

    st.stop()
