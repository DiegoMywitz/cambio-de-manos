import base64
import os
import uuid

import requests
import streamlit as st
from supabase import create_client

BUCKET = "publicaciones"


def _config(key: str, default=None):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


SUPABASE_URL = _config("SUPABASE_URL")
SUPABASE_SERVICE_KEY = _config("SUPABASE_SERVICE_KEY")
VISION_API_KEY = _config("CDM_VISION_API_KEY")

NIVELES_BLOQUEADOS = {"LIKELY", "VERY_LIKELY"}
MOTIVOS_SAFE_SEARCH = {
    "adult": "contenido para adultos",
    "violence": "contenido violento",
    "medical": "contenido gráfico/médico",
}


def esta_configurado() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)


def moderacion_configurada() -> bool:
    return bool(VISION_API_KEY)


def imagen_es_apta(contenido: bytes) -> tuple[bool, str]:
    """Chequea una foto con Google Cloud Vision (SafeSearch) antes de publicarla.

    Si la moderación no está configurada, o si la llamada a la API falla (caída del
    servicio, cuota agotada, etc.), no bloqueamos la publicación — el botón de
    "Reportar esta publicación" queda como respaldo para lo que se escape. Devuelve
    (apta, motivo_de_rechazo)."""
    if not moderacion_configurada():
        return True, ""
    try:
        resp = requests.post(
            f"https://vision.googleapis.com/v1/images:annotate?key={VISION_API_KEY}",
            json={"requests": [{
                "image": {"content": base64.b64encode(contenido).decode("ascii")},
                "features": [{"type": "SAFE_SEARCH_DETECTION"}],
            }]},
            timeout=15,
        )
        resp.raise_for_status()
        anotacion = resp.json()["responses"][0].get("safeSearchAnnotation", {})
        for campo, motivo in MOTIVOS_SAFE_SEARCH.items():
            if anotacion.get(campo) in NIVELES_BLOQUEADOS:
                return False, motivo
        return True, ""
    except Exception as e:
        print(f"[images] Falló la moderación de imagen (se deja pasar): {e!r}")
        return True, ""


def _client():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def subir_imagen(pub_id: int, contenido: bytes, nombre_original: str) -> str:
    """Sube una imagen al bucket de Supabase Storage y devuelve su URL pública."""
    extension = nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else "jpg"
    ruta = f"{pub_id}/{uuid.uuid4().hex}.{extension}"
    client = _client()
    client.storage.from_(BUCKET).upload(
        ruta, contenido, {"content-type": f"image/{extension}"}
    )
    return client.storage.from_(BUCKET).get_public_url(ruta)


def subir_video(pub_id: int, contenido: bytes, nombre_original: str) -> str:
    """Sube un video corto al bucket de Supabase Storage y devuelve su URL pública."""
    extension = nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else "mp4"
    ruta = f"{pub_id}/video/{uuid.uuid4().hex}.{extension}"
    client = _client()
    client.storage.from_(BUCKET).upload(
        ruta, contenido, {"content-type": f"video/{extension}"}
    )
    return client.storage.from_(BUCKET).get_public_url(ruta)
