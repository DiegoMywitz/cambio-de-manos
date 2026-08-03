import os
import uuid

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


def esta_configurado() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)


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
