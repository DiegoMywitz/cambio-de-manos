import hashlib
import os

import psycopg2
import psycopg2.extras
import streamlit as st

RUBROS = [
    "Gastronomía", "Comercio minorista", "Indumentaria", "Servicios",
    "Industria / Fábrica", "Salud y belleza", "Tecnología", "Educación",
    "Inmobiliario", "Transporte y logística", "Agropecuario", "Otro",
]

PROVINCIAS = [
    "Buenos Aires", "CABA", "Córdoba", "Santa Fe", "Mendoza", "Tucumán",
    "Entre Ríos", "Salta", "Chaco", "Corrientes", "Misiones", "San Juan",
    "Jujuy", "Río Negro", "Neuquén", "Formosa", "Chubut", "San Luis",
    "Catamarca", "La Rioja", "La Pampa", "Santiago del Estero",
    "Santa Cruz", "Tierra del Fuego",
]

CIUDADES_SUGERIDAS = [
    "CABA - Palermo", "CABA - Recoleta", "CABA - Belgrano", "CABA - Caballito",
    "CABA - Villa Urquiza", "CABA - Flores", "CABA - Almagro", "CABA - Once",
    "La Plata", "Mar del Plata", "Quilmes", "Avellaneda", "San Isidro",
    "Tigre", "Morón", "Lanús", "Bahía Blanca", "Córdoba Capital", "Villa María",
    "Río Cuarto", "Rosario", "Santa Fe Capital", "Rafaela", "Mendoza Capital",
    "San Rafael", "San Miguel de Tucumán", "Salta Capital", "San Salvador de Jujuy",
    "Resistencia", "Corrientes Capital", "Posadas", "Neuquén Capital",
    "Comodoro Rivadavia", "Bariloche", "Viedma", "Santa Rosa", "Paraná",
    "Concordia", "San Juan Capital", "San Luis Capital", "Santiago del Estero Capital",
    "Río Gallegos", "Ushuaia", "Formosa Capital", "Catamarca Capital", "La Rioja Capital",
]


def _database_url() -> str:
    try:
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Falta configurar DATABASE_URL (cadena de conexión a Postgres). "
            "Definila como variable de entorno o en .streamlit/secrets.toml."
        )
    return url


def get_connection():
    conn = psycopg2.connect(_database_url(), cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefono TEXT,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS publicaciones (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            titulo TEXT NOT NULL,
            rubro TEXT NOT NULL,
            provincia TEXT NOT NULL,
            localidad TEXT,
            descripcion TEXT,
            precio_venta DOUBLE PRECISION,
            facturacion_mensual DOUBLE PRECISION,
            resultado_mensual DOUBLE PRECISION,
            antiguedad_anios INTEGER,
            empleados INTEGER,
            incluye_inmueble INTEGER DEFAULT 0,
            motivo_venta TEXT,
            estado TEXT DEFAULT 'activa',
            tier TEXT DEFAULT 'basico',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        ALTER TABLE publicaciones ADD COLUMN IF NOT EXISTS tier TEXT DEFAULT 'basico';

        CREATE TABLE IF NOT EXISTS consultas (
            id SERIAL PRIMARY KEY,
            publicacion_id INTEGER NOT NULL REFERENCES publicaciones(id),
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            mensaje TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS imagenes_publicacion (
            id SERIAL PRIMARY KEY,
            publicacion_id INTEGER NOT NULL REFERENCES publicaciones(id),
            url TEXT NOT NULL,
            orden INTEGER DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


def _hash_password(password: str, salt: str = None) -> tuple:
    salt = salt or os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()
    return hashed, salt


def crear_usuario(nombre: str, email: str, password: str, telefono: str = None) -> int:
    hashed, salt = _hash_password(password)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (nombre, email, telefono, password_hash, password_salt) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (nombre, email.lower().strip(), telefono, hashed, salt),
        )
        new_id = cur.fetchone()["id"]
        conn.commit()
        cur.close()
        return new_id
    finally:
        conn.close()


def obtener_usuario_por_email(email: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email.lower().strip(),))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def obtener_usuario(usuario_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def verificar_password(usuario, password: str) -> bool:
    hashed, _ = _hash_password(password, usuario["password_salt"])
    return hashed == usuario["password_hash"]


def crear_publicacion(data: dict, estado: str = "activa", tier: str = "basico") -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO publicaciones (
            usuario_id, titulo, rubro, provincia, localidad, descripcion,
            precio_venta, facturacion_mensual, resultado_mensual,
            antiguedad_anios, empleados, incluye_inmueble, motivo_venta, estado, tier
        ) VALUES (%(usuario_id)s, %(titulo)s, %(rubro)s, %(provincia)s, %(localidad)s, %(descripcion)s,
            %(precio_venta)s, %(facturacion_mensual)s, %(resultado_mensual)s,
            %(antiguedad_anios)s, %(empleados)s, %(incluye_inmueble)s, %(motivo_venta)s, %(estado)s, %(tier)s)
        RETURNING id
        """,
        {**data, "estado": estado, "tier": tier},
    )
    new_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return new_id


def activar_publicacion(pub_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE publicaciones SET estado = 'activa' WHERE id = %s", (pub_id,))
    conn.commit()
    cur.close()
    conn.close()


_SELECT_PUB_CON_CONTACTO = """
    SELECT p.*, u.nombre AS nombre_contacto, u.email AS email_contacto,
           u.telefono AS telefono_contacto
    FROM publicaciones p
    JOIN usuarios u ON u.id = p.usuario_id
"""


def listar_publicaciones(rubro=None, provincia=None, precio_max=None, texto=None):
    conn = get_connection()
    cur = conn.cursor()
    query = _SELECT_PUB_CON_CONTACTO + " WHERE p.estado = 'activa'"
    params = []

    if rubro and rubro != "Todos":
        query += " AND p.rubro = %s"
        params.append(rubro)
    if provincia and provincia != "Todas":
        query += " AND p.provincia = %s"
        params.append(provincia)
    if precio_max:
        query += " AND (p.precio_venta IS NULL OR p.precio_venta <= %s)"
        params.append(precio_max)
    if texto:
        query += " AND (p.titulo ILIKE %s OR p.descripcion ILIKE %s)"
        like = f"%{texto}%"
        params.extend([like, like])

    query += " ORDER BY (p.tier = 'destacado') DESC, p.fecha_creacion DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def obtener_publicacion(pub_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT_PUB_CON_CONTACTO + " WHERE p.id = %s", (pub_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def listar_publicaciones_de_usuario(usuario_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        _SELECT_PUB_CON_CONTACTO + " WHERE p.usuario_id = %s ORDER BY p.fecha_creacion DESC",
        (usuario_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def crear_consulta(data: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO consultas (publicacion_id, usuario_id, mensaje)
        VALUES (%(publicacion_id)s, %(usuario_id)s, %(mensaje)s)
        """,
        data,
    )
    conn.commit()
    cur.close()
    conn.close()


def listar_consultas(pub_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.*, u.nombre AS nombre_interesado, u.email AS email_interesado,
               u.telefono AS telefono_interesado
        FROM consultas c
        JOIN usuarios u ON u.id = c.usuario_id
        WHERE c.publicacion_id = %s
        ORDER BY c.fecha_creacion DESC
        """,
        (pub_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def agregar_imagen(pub_id: int, url: str, orden: int = 0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO imagenes_publicacion (publicacion_id, url, orden) VALUES (%s, %s, %s)",
        (pub_id, url, orden),
    )
    conn.commit()
    cur.close()
    conn.close()


def listar_imagenes(pub_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM imagenes_publicacion WHERE publicacion_id = %s ORDER BY orden, id",
        (pub_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def imagenes_portada(pub_ids: list):
    """Devuelve un dict {publicacion_id: primera_url} para una lista de ids, en una sola consulta."""
    if not pub_ids:
        return {}
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT ON (publicacion_id) publicacion_id, url
        FROM imagenes_publicacion
        WHERE publicacion_id = ANY(%s)
        ORDER BY publicacion_id, orden, id
        """,
        (pub_ids,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {r["publicacion_id"]: r["url"] for r in rows}
