"""Job standalone para vencer las publicaciones que usaron el cupo de lanzamiento
(primeros N negocios gratis por un mes): las manda a "pendiente_pago" cuando se
cumple el plazo y avisa por email al dueño.

Se debe programar aparte, igual que alertas_job.py (Programador de tareas de
Windows corriendo `python promo_vencida_job.py` una vez por día alcanza,
porque el plazo se mide en días, no en horas).

Necesita las mismas variables de entorno que la app (DATABASE_URL, CDM_SMTP_*),
seteadas en el entorno donde corra el script (no lee .streamlit/secrets.toml).
"""

from database import publicaciones_promo_vencidas, cambiar_estado_publicacion
import notifications


def main():
    vencidas = publicaciones_promo_vencidas()
    print(f"Revisando {len(vencidas)} publicación(es) con promo gratis vencida...")

    for pub in vencidas:
        cambiar_estado_publicacion(pub["id"], "pendiente_pago")
        enviado = notifications.notificar_promo_vencida(pub["email"], pub["nombre"], pub["titulo"], pub["id"])
        print(f"Publicación #{pub['id']} ({pub['titulo']!r}): pausada, aviso enviado={enviado}")

    print("Listo.")


if __name__ == "__main__":
    main()
