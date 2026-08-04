import os

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
PRECIO_PUBLICACION = float(_config("CDM_PRECIO_PUBLICACION", "9999"))
PRECIO_DESTACADO = float(_config("CDM_PRECIO_DESTACADO", "19999"))
APP_BASE_URL = _config("CDM_APP_BASE_URL", "http://localhost:8600")

PRECIOS_POR_TIER = {"basico": PRECIO_PUBLICACION, "destacado": PRECIO_DESTACADO}


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
                "unit_price": PRECIOS_POR_TIER.get(tier, PRECIO_PUBLICACION),
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
