"""Job standalone para enviar emails de alertas de búsqueda.

Streamlit Cloud no ejecuta procesos en segundo plano, así que este script se
debe programar aparte (por ejemplo con el Programador de tareas de Windows,
corriendo `python alertas_job.py` una vez por hora o una vez al día).

Necesita las mismas variables de entorno que la app (DATABASE_URL, CDM_SMTP_*),
seteadas en el entorno donde corra el script (no lee .streamlit/secrets.toml).
"""

from database import listar_todas_las_alertas, publicaciones_nuevas_para_alerta, actualizar_ultima_revision
import notifications


def main():
    if not notifications.esta_configurado():
        print("Notificaciones por email no configuradas (faltan CDM_SMTP_*). Nada para hacer.")
        return

    alertas = listar_todas_las_alertas()
    print(f"Revisando {len(alertas)} alerta(s)...")

    for alerta in alertas:
        nuevas = publicaciones_nuevas_para_alerta(alerta)
        if nuevas:
            enviado = notifications.notificar_alerta_busqueda(alerta["email"], alerta["nombre"], nuevas)
            print(f"Alerta #{alerta['id']} ({alerta['email']}): {len(nuevas)} nueva(s), enviado={enviado}")
        actualizar_ultima_revision(alerta["id"])

    print("Listo.")


if __name__ == "__main__":
    main()
