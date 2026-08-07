import contextlib
import os
import smtplib
import socket
import ssl
from email.message import EmailMessage

import streamlit as st


@contextlib.contextmanager
def _forzar_ipv4():
    """Fuerza resolución DNS a IPv4 para la conexión SMTP.

    Render (y otros hosts en contenedores) a veces resuelven smtp.gmail.com a una
    dirección IPv6 sin salida funcional en el contenedor, lo que produce
    OSError(101, 'Network is unreachable') aunque las credenciales sean correctas.
    """
    original = socket.getaddrinfo

    def _solo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
        return original(host, port, socket.AF_INET, type, proto, flags)

    socket.getaddrinfo = _solo_ipv4
    try:
        yield
    finally:
        socket.getaddrinfo = original


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
ADMIN_EMAIL = _config("CDM_ADMIN_EMAIL", "cambiodefirma.contacto@gmail.com")


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
        with _forzar_ipv4():
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls(context=context)
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        return True
    except Exception as e:
        # No relanzamos (una falla de notificación no debe romper el flujo de la app),
        # pero sí lo logueamos: antes fallaba en silencio total y no había forma de
        # diagnosticar por qué a un usuario nunca le llegaba un email.
        print(f"[notifications] Falló el envío a {destinatario!r} ({asunto!r}): {e!r}")
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


def notificar_consulta_respondida(email_interesado: str, nombre_interesado: str,
                                   titulo_publicacion: str, nombre_vendedor: str) -> bool:
    asunto = f"Cambio de Manos: el vendedor respondió tu consulta por '{titulo_publicacion}'"
    cuerpo = (
        f"Hola {nombre_interesado},\n\n"
        f"{nombre_vendedor}, vendedor de \"{titulo_publicacion}\", marcó tu consulta como respondida. "
        "Es probable que se haya puesto en contacto por teléfono, email o WhatsApp con los datos que dejaste.\n\n"
        "Si todavía no tuviste noticias, podés escribirle directamente con los datos de contacto de la publicación."
    )
    return enviar_email(email_interesado, asunto, cuerpo)


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
        f"Para elegir una nueva contraseña, ingresá a este link (válido por 24 horas):\n{link}\n\n"
        "Si vos no pediste esto, podés ignorar este email: tu contraseña actual sigue funcionando."
    )
    return enviar_email(email, asunto, cuerpo)


def notificar_reporte_publicacion(pub_id: int, titulo: str, motivo: str, detalle: str,
                                   email_reportante: str = "") -> bool:
    asunto = f"Cambio de Manos: reporte de publicación #{pub_id}"
    cuerpo = (
        f"Alguien reportó la publicación #{pub_id} ({titulo}).\n\n"
        f"Motivo: {motivo}\n"
        f"Detalle: {detalle or '(sin detalle)'}\n"
        f"Contacto de quien reporta: {email_reportante or '(no informado)'}\n\n"
        f"Revisala en: {_config('CDM_APP_BASE_URL', '').rstrip('/')}/?p=negocio&id={pub_id}"
    )
    return enviar_email(ADMIN_EMAIL, asunto, cuerpo)
