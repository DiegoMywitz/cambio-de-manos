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


def notificar_verificacion_email(email: str, nombre: str, link: str) -> bool:
    asunto = "Cambio de Manos: confirmá tu email"
    cuerpo = (
        f"Hola {nombre},\n\n"
        "Gracias por crear tu cuenta en Cambio de Manos. Para confirmar tu email, ingresá a este link:\n"
        f"{link}\n\n"
        "Si vos no creaste esta cuenta, podés ignorar este email."
    )
    return enviar_email(email, asunto, cuerpo)


def notificar_alerta_busqueda(email: str, nombre: str, publicaciones: list) -> bool:
    asunto = f"Cambio de Manos: {len(publicaciones)} negocio(s) nuevo(s) que te pueden interesar"
    lineas = [f"Hola {nombre},\n", "Aparecieron negocios nuevos que coinciden con una búsqueda que guardaste:\n"]
    for pub in publicaciones:
        precio = f"${pub['precio_venta']:,.0f}".replace(",", ".") if pub["precio_venta"] else "Precio no especificado"
        lineas.append(f"- {pub['titulo']} ({pub['rubro']}, {pub['provincia']}) — {precio}")
    lineas.append("\nIngresá a Cambio de Manos para ver el detalle y dejar tu consulta.")
    cuerpo = "\n".join(lineas)
    return enviar_email(email, asunto, cuerpo)


def notificar_reset_password(email: str, nombre: str, link: str) -> bool:
    asunto = "Cambio de Manos: recuperar tu contraseña"
    cuerpo = (
        f"Hola {nombre},\n\n"
        "Recibimos un pedido para restablecer tu contraseña en Cambio de Manos.\n\n"
        f"Para elegir una nueva contraseña, ingresá a este link (válido por 1 hora):\n{link}\n\n"
        "Si vos no pediste esto, podés ignorar este email: tu contraseña actual sigue funcionando."
    )
    return enviar_email(email, asunto, cuerpo)
