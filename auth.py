import re

import streamlit as st
import streamlit.components.v1 as components

from database import (
    crear_usuario, obtener_usuario_por_email, verificar_password,
    crear_token_reset, obtener_reset_valido, actualizar_password_con_token,
    crear_token_verificacion, verificar_email_con_token,
    diagnosticar_token_reset,
    crear_sesion, obtener_usuario_por_sesion, eliminar_sesion,
)
import notifications
import legal
import payments

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
APP_URL = payments.APP_BASE_URL


def usuario_actual():
    return st.session_state.get("usuario")


def _guardar_sesion_local(token: str):
    """Guarda el token de sesión en localStorage del navegador para que el login
    sobreviva a un F5 (st.session_state solo se pierde en cada reconexión)."""
    components.html(
        f"<script>window.parent.localStorage.setItem('cdm_st', '{token}');</script>",
        height=0, width=0,
    )


def _borrar_sesion_local():
    components.html(
        "<script>window.parent.localStorage.removeItem('cdm_st');</script>",
        height=0, width=0,
    )


def _iniciar_sesion(usuario: dict):
    """Marca a un usuario como logueado y le da persistencia entre recargas."""
    st.session_state.usuario = usuario
    token = crear_sesion(usuario["id"])
    st.session_state._session_token = token
    _guardar_sesion_local(token)


def restaurar_sesion():
    """Si el usuario no está logueado en esta sesión de Streamlit (por ejemplo,
    porque recargó la página), intenta restaurar el login usando el token
    guardado en localStorage la vez anterior."""
    if usuario_actual():
        return

    token_qp = st.query_params.get("st")
    if token_qp:
        usuario = obtener_usuario_por_sesion(token_qp)
        otros_params = {k: v for k, v in st.query_params.items() if k != "st"}
        st.query_params.clear()
        for k, v in otros_params.items():
            st.query_params[k] = v
        if usuario:
            st.session_state.usuario = dict(usuario)
            st.session_state._session_token = token_qp
        else:
            _borrar_sesion_local()
        st.rerun()
        return

    components.html(
        """
        <script>
        var t = window.parent.localStorage.getItem('cdm_st');
        if (t) {
            var url = new URL(window.parent.location.href);
            url.searchParams.set('st', t);
            window.parent.location.replace(url.toString());
        }
        </script>
        """,
        height=0, width=0,
    )


def reenviar_verificacion(usuario) -> bool:
    """Genera un nuevo link de verificación y lo reenvía. Devuelve True si se pudo enviar."""
    if not notifications.esta_configurado():
        return False
    token = crear_token_verificacion(usuario["id"])
    link = f"{APP_URL}?verify_token={token}"
    return notifications.notificar_verificacion_email(usuario["email"], usuario["nombre"], link)


def cerrar_sesion():
    token = st.session_state.get("_session_token")
    if token:
        eliminar_sesion(token)
    st.session_state.usuario = None
    st.session_state._session_token = None
    _borrar_sesion_local()


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
                _iniciar_sesion(dict(usuario))
                st.rerun()


def _form_olvide_password():
    with st.form("form_olvide_password"):
        email = st.text_input("Email de tu cuenta")
        enviar = st.form_submit_button("Enviar link de recuperación", use_container_width=True)

        if enviar:
            st.session_state.mostrar_olvide_pass = True
            usuario = obtener_usuario_por_email(email)
            envio_fallo = False
            if usuario is not None:
                token = crear_token_reset(usuario["id"])
                link = f"{APP_URL}?reset_token={token}"
                print(f"[auth] Link de recuperación generado para {usuario['email']}: {token[:8]}...")
                if notifications.esta_configurado():
                    envio_fallo = not notifications.notificar_reset_password(
                        usuario["email"], usuario["nombre"], link
                    )
                else:
                    st.info(f"Notificaciones por email no configuradas. Link de prueba: {link}")
            if envio_fallo:
                # Acá sí distinguimos del caso "el email no existe": si la cuenta existe
                # pero el envío falló (problema de SMTP, etc.), decirle "éxito" igual
                # dejaba al usuario sin ninguna forma de recuperar la contraseña.
                st.error(
                    "Encontramos tu cuenta pero no pudimos enviarte el email ahora mismo. "
                    "Escribinos a **cambiodefirma.contacto@gmail.com** y te ayudamos a recuperar el acceso."
                )
            else:
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
        print(f"[auth] Link de recuperación rechazado ({token[:8]}...): {diagnosticar_token_reset(token)}")
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
                _iniciar_sesion(dict(obtener_usuario_por_email(email)))
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
        with st.expander("¿Olvidaste tu contraseña?", expanded=st.session_state.get("mostrar_olvide_pass", False)):
            _form_olvide_password()
    with tab_registro:
        _form_registro()

    st.stop()
