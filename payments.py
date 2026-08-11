import os
from datetime import date

import mercadopago
import streamlit as st


def _config(key: str, default=None):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


ACCESS_TOKEN = _config("CDM_MP_ACCESS_TOKEN")

# Básico: precio de lanzamiento hasta CDM_PROMO_BASICO_HASTA (inclusive), después
# pasa al precio estándar. Fecha configurable por si el lanzamiento se corre.
PRECIO_BASICO_PROMO = float(_config("CDM_PRECIO_BASICO_PROMO", "9999"))
PRECIO_BASICO_ESTANDAR = float(_config("CDM_PRECIO_BASICO_ESTANDAR", "23999"))
PROMO_BASICO_HASTA = _config("CDM_PROMO_BASICO_HASTA", "2026-10-04")
PRECIO_DESTACADO = float(_config("CDM_PRECIO_DESTACADO", "54000"))

APP_BASE_URL = _config("CDM_APP_BASE_URL", "http://localhost:8600")

CUPO_PROMO_GRATIS = int(_config("CDM_CUPO_PROMO_GRATIS", "300"))
DIAS_PROMO_GRATIS = int(_config("CDM_DIAS_PROMO_GRATIS", "30"))


def precio_basico_vigente() -> float:
    """Precio del nivel Básico hoy: el de lanzamiento mientras dure la promo,
    después el estándar. Sin fecha configurada, va directo al estándar."""
    if PROMO_BASICO_HASTA:
        try:
            limite = date.fromisoformat(PROMO_BASICO_HASTA)
            if date.today() <= limite:
                return PRECIO_BASICO_PROMO
        except ValueError:
            pass
    return PRECIO_BASICO_ESTANDAR


def precios_por_tier() -> dict:
    return {"basico": precio_basico_vigente(), "destacado": PRECIO_DESTACADO}


def esta_configurado() -> bool:
    return bool(ACCESS_TOKEN)


def _sdk():
    return mercadopago.SDK(ACCESS_TOKEN)


def crear_preferencia_publicacion(pub_id: int, titulo: str, tier: str = "basico") -> str:
    """Crea una preferencia de pago para publicar un negocio y devuelve la URL de checkout."""
    sdk = _sdk()
    etiqueta_tier = "Destacado" if tier == "destacado" else "Básico"
    preference_data = {
        "items": [
            {
                "title": f"Publicación {etiqueta_tier} en Cambio de Manos: {titulo}"[:250],
                "quantity": 1,
                "unit_price": precios_por_tier().get(tier, precio_basico_vigente()),
                "currency_id": "ARS",
            }
        ],
        "external_reference": str(pub_id),
        "back_urls": {
            "success": f"{APP_BASE_URL.rstrip('/')}/?p=publicar&pago_id={pub_id}",
            "pending": f"{APP_BASE_URL.rstrip('/')}/?p=publicar&pago_id={pub_id}",
            "failure": f"{APP_BASE_URL.rstrip('/')}/?p=publicar&pago_id={pub_id}",
        },
    }
    result = sdk.preference().create(preference_data)
    preference = result["response"]
    return preference["init_point"]


def verificar_pago_aprobado(pub_id: int) -> bool:
    """Busca pagos asociados a la publicación y devuelve True si hay alguno aprobado."""
    sdk = _sdk()
    result = sdk.payment().search({"external_reference": str(pub_id)})
    pagos = result.get("response", {}).get("results", [])
    return any(p.get("status") == "approved" for p in pagos)
