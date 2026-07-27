import os
import smtplib
import ssl
from email.message import EmailMessage

import streamlit as st


def _config(key: str, default=None):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


SMTP_HOST = _config("CDM_SMTP_HOST")
SMTP_PORT = int(_config("CDM_SMTP_PORT", "587"))
SMTP_USER = _config("CDM_SMTP_USER")
SMTP_PASSWORD = _config("CDM_SMTP_PASSWORD")
FROM_ADDRESS = _config("CDM_FROM_ADDRESS", SMTP_USER)


def esta_configurado() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def enviar_email(destinatario: str, asunto: str, cuerpo: str) -> bool:
    """Envía un email. Devuelve True si se envió, False si no está configurado o falló.
    Nunca lanza una excepción: una falla de notificación no debe romper el flujo de la app."""
    if not esta_configurado():
        return False

    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = FROM_ADDRESS
    msg["To"] = destinatario
    msg.set_content(cuerpo)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        return False


def notificar_nueva_consulta(email_vendedor: str, titulo_publicacion: str,
                              nombre_interesado: str, mensaje: str) -> bool:
    asunto = f"Cambio de Manos: nueva consulta por '{titulo_publicacion}'"
    cuerpo = (
        f"Recibiste una nueva consulta por tu publicación \"{titulo_publicacion}\".\n\n"
        f"Interesado: {nombre_interesado}\n"
        f"Mensaje: {mensaje or '(sin mensaje)'}\n\n"
        "Ingresá a Cambio de Manos, sección 'Mis publicaciones', para ver los datos de contacto."
    )
    return enviar_email(email_vendedor, asunto, cuerpo)
