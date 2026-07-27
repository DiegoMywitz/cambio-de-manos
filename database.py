import hashlib
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "cambio_de_manos.db"

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


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefono TEXT,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS publicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            rubro TEXT NOT NULL,
            provincia TEXT NOT NULL,
            localidad TEXT,
            descripcion TEXT,
            precio_venta REAL,
            facturacion_mensual REAL,
            resultado_mensual REAL,
            antiguedad_anios INTEGER,
            empleados INTEGER,
            incluye_inmueble INTEGER DEFAULT 0,
            motivo_venta TEXT,
            estado TEXT DEFAULT 'activa',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publicacion_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            mensaje TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (publicacion_id) REFERENCES publicaciones(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
        """
    )
    conn.commit()
    conn.close()


def _hash_password(password: str, salt: str = None) -> tuple:
    salt = salt or os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()
    return hashed, salt


def crear_usuario(nombre: str, email: str, password: str, telefono: str = None) -> int:
    hashed, salt = _hash_password(password)
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO usuarios (nombre, email, telefono, password_hash, password_salt) VALUES (?, ?, ?, ?, ?)",
            (nombre, email.lower().strip(), telefono, hashed, salt),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def obtener_usuario_por_email(email: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE email = ?", (email.lower().strip(),)
    ).fetchone()
    conn.close()
    return row


def obtener_usuario(usuario_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    conn.close()
    return row


def verificar_password(usuario, password: str) -> bool:
    hashed, _ = _hash_password(password, usuario["password_salt"])
    return hashed == usuario["password_hash"]


def crear_publicacion(data: dict, estado: str = "activa") -> int:
    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO publicaciones (
            usuario_id, titulo, rubro, provincia, localidad, descripcion,
            precio_venta, facturacion_mensual, resultado_mensual,
            antiguedad_anios, empleados, incluye_inmueble, motivo_venta, estado
        ) VALUES (:usuario_id, :titulo, :rubro, :provincia, :localidad, :descripcion,
            :precio_venta, :facturacion_mensual, :resultado_mensual,
            :antiguedad_anios, :empleados, :incluye_inmueble, :motivo_venta, :estado)
        """,
        {**data, "estado": estado},
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def activar_publicacion(pub_id: int):
    conn = get_connection()
    conn.execute("UPDATE publicaciones SET estado = 'activa' WHERE id = ?", (pub_id,))
    conn.commit()
    conn.close()


_SELECT_PUB_CON_CONTACTO = """
    SELECT p.*, u.nombre AS nombre_contacto, u.email AS email_contacto,
           u.telefono AS telefono_contacto
    FROM publicaciones p
    JOIN usuarios u ON u.id = p.usuario_id
"""


def listar_publicaciones(rubro=None, provincia=None, precio_max=None, texto=None):
    conn = get_connection()
    query = _SELECT_PUB_CON_CONTACTO + " WHERE p.estado = 'activa'"
    params = []

    if rubro and rubro != "Todos":
        query += " AND p.rubro = ?"
        params.append(rubro)
    if provincia and provincia != "Todas":
        query += " AND p.provincia = ?"
        params.append(provincia)
    if precio_max:
        query += " AND (p.precio_venta IS NULL OR p.precio_venta <= ?)"
        params.append(precio_max)
    if texto:
        query += " AND (p.titulo LIKE ? OR p.descripcion LIKE ?)"
        like = f"%{texto}%"
        params.extend([like, like])

    query += " ORDER BY p.fecha_creacion DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def obtener_publicacion(pub_id: int):
    conn = get_connection()
    row = conn.execute(
        _SELECT_PUB_CON_CONTACTO + " WHERE p.id = ?", (pub_id,)
    ).fetchone()
    conn.close()
    return row


def listar_publicaciones_de_usuario(usuario_id: int):
    conn = get_connection()
    rows = conn.execute(
        _SELECT_PUB_CON_CONTACTO + " WHERE p.usuario_id = ? ORDER BY p.fecha_creacion DESC",
        (usuario_id,),
    ).fetchall()
    conn.close()
    return rows


def crear_consulta(data: dict):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO consultas (publicacion_id, usuario_id, mensaje)
        VALUES (:publicacion_id, :usuario_id, :mensaje)
        """,
        data,
    )
    conn.commit()
    conn.close()


def listar_consultas(pub_id: int):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT c.*, u.nombre AS nombre_interesado, u.email AS email_interesado,
               u.telefono AS telefono_interesado
        FROM consultas c
        JOIN usuarios u ON u.id = c.usuario_id
        WHERE c.publicacion_id = ?
        ORDER BY c.fecha_creacion DESC
        """,
        (pub_id,),
    ).fetchall()
    conn.close()
    return rows
