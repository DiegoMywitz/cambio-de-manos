import hashlib
import os
import secrets

import psycopg2
import psycopg2.extras
import psycopg2.pool
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


@st.cache_resource(show_spinner=False)
def _get_pool():
    """Pool de conexiones reutilizables, compartido entre todas las sesiones del
    mismo proceso. Antes cada consulta abría y cerraba su propia conexión a
    Supabase de cero (handshake + SSL + login), algo lento en un servidor con
    poca CPU. cache_resource hace que el pool se cree una sola vez por proceso."""
    return psycopg2.pool.ThreadedConnectionPool(
        1, 10, _database_url(), cursor_factory=psycopg2.extras.RealDictCursor,
    )


def get_connection():
    return _get_pool().getconn()


def release_connection(conn):
    try:
        _get_pool().putconn(conn)
    except Exception:
        try:
            conn.close()
        except Exception:
            pass


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
            email_verificado BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email_verificado BOOLEAN DEFAULT FALSE;

        CREATE TABLE IF NOT EXISTS verificaciones_email (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            token TEXT NOT NULL UNIQUE,
            usado BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_expiracion TIMESTAMP NOT NULL
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
            es_franquicia BOOLEAN DEFAULT FALSE,
            fecha_venta TIMESTAMP,
            video_url TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        ALTER TABLE publicaciones ADD COLUMN IF NOT EXISTS tier TEXT DEFAULT 'basico';
        ALTER TABLE publicaciones ADD COLUMN IF NOT EXISTS es_franquicia BOOLEAN DEFAULT FALSE;
        ALTER TABLE publicaciones ADD COLUMN IF NOT EXISTS fecha_venta TIMESTAMP;
        ALTER TABLE publicaciones ADD COLUMN IF NOT EXISTS video_url TEXT;
        ALTER TABLE publicaciones ADD COLUMN IF NOT EXISTS promo_gratis BOOLEAN DEFAULT FALSE;
        ALTER TABLE publicaciones ADD COLUMN IF NOT EXISTS fecha_fin_promo_gratis TIMESTAMP;

        CREATE TABLE IF NOT EXISTS consultas (
            id SERIAL PRIMARY KEY,
            publicacion_id INTEGER NOT NULL REFERENCES publicaciones(id),
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            mensaje TEXT,
            respondida BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        ALTER TABLE consultas ADD COLUMN IF NOT EXISTS respondida BOOLEAN DEFAULT FALSE;

        CREATE TABLE IF NOT EXISTS imagenes_publicacion (
            id SERIAL PRIMARY KEY,
            publicacion_id INTEGER NOT NULL REFERENCES publicaciones(id),
            url TEXT NOT NULL,
            orden INTEGER DEFAULT 0,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS favoritos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            publicacion_id INTEGER NOT NULL REFERENCES publicaciones(id),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (usuario_id, publicacion_id)
        );

        CREATE TABLE IF NOT EXISTS alertas_busqueda (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            rubro TEXT,
            provincia TEXT,
            precio_max DOUBLE PRECISION,
            texto TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultima_revision TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS password_resets (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            token TEXT NOT NULL UNIQUE,
            usado BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_expiracion TIMESTAMP NOT NULL
        );
        """
    )
    conn.commit()
    cur.close()
    release_connection(conn)


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
        release_connection(conn)


def obtener_usuario_por_email(email: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email.lower().strip(),))
    row = cur.fetchone()
    cur.close()
    release_connection(conn)
    return row


def obtener_usuario(usuario_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
    row = cur.fetchone()
    cur.close()
    release_connection(conn)
    return row


def verificar_password(usuario, password: str) -> bool:
    hashed, _ = _hash_password(password, usuario["password_salt"])
    return hashed == usuario["password_hash"]


def crear_token_verificacion(usuario_id: int, horas_validez: int = 48) -> str:
    token = secrets.token_urlsafe(32)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO verificaciones_email (usuario_id, token, fecha_expiracion)
        VALUES (%s, %s, NOW() + %s * INTERVAL '1 hour')
        """,
        (usuario_id, token, horas_validez),
    )
    conn.commit()
    cur.close()
    release_connection(conn)
    return token


def verificar_email_con_token(token: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM verificaciones_email
        WHERE token = %s AND usado = FALSE AND fecha_expiracion > NOW()
        """,
        (token,),
    )
    row = cur.fetchone()
    if row is None:
        cur.close()
        release_connection(conn)
        return False

    cur.execute("UPDATE usuarios SET email_verificado = TRUE WHERE id = %s", (row["usuario_id"],))
    cur.execute("UPDATE verificaciones_email SET usado = TRUE WHERE token = %s", (token,))
    conn.commit()
    cur.close()
    release_connection(conn)
    return True


def crear_token_reset(usuario_id: int, horas_validez: int = 24) -> str:
    token = secrets.token_urlsafe(32)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO password_resets (usuario_id, token, fecha_expiracion)
        VALUES (%s, %s, NOW() + %s * INTERVAL '1 hour')
        """,
        (usuario_id, token, horas_validez),
    )
    conn.commit()
    cur.close()
    release_connection(conn)
    return token


def obtener_reset_valido(token: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.*, u.email, u.nombre FROM password_resets r
        JOIN usuarios u ON u.id = r.usuario_id
        WHERE r.token = %s AND r.usado = FALSE AND r.fecha_expiracion > NOW()
        """,
        (token,),
    )
    row = cur.fetchone()
    cur.close()
    release_connection(conn)
    return row


def diagnosticar_token_reset(token: str) -> str:
    """Para loguear por qué un link de recuperación no sirvió: no existe, ya se
    usó, o venció. Sin esto un token inválido siempre daba el mismo mensaje
    genérico y no había forma de saber cuál de los tres casos era."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT usado, fecha_expiracion, fecha_expiracion > NOW() AS vigente "
        "FROM password_resets WHERE token = %s",
        (token,),
    )
    row = cur.fetchone()
    cur.close()
    release_connection(conn)
    if row is None:
        return "no existe ese token"
    if row["usado"]:
        return f"ya estaba usado (expiraba {row['fecha_expiracion']})"
    if not row["vigente"]:
        return f"venció (expiraba {row['fecha_expiracion']})"
    return "válido (inesperado que haya fallado)"


def actualizar_password_con_token(token: str, password_nueva: str) -> bool:
    reset = obtener_reset_valido(token)
    if reset is None:
        return False
    hashed, salt = _hash_password(password_nueva)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE usuarios SET password_hash = %s, password_salt = %s WHERE id = %s",
        (hashed, salt, reset["usuario_id"]),
    )
    cur.execute("UPDATE password_resets SET usado = TRUE WHERE token = %s", (token,))
    conn.commit()
    cur.close()
    release_connection(conn)
    return True


def publicacion_duplicada_reciente(usuario_id: int, titulo: str, precio_venta, segundos: int = 120):
    """Evita altas duplicadas si se toca el botón de publicar varias veces seguidas
    (por ejemplo, porque la carga tarda y el usuario reintenta)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id FROM publicaciones
        WHERE usuario_id = %s AND titulo = %s AND precio_venta = %s
          AND fecha_creacion > NOW() - %s * INTERVAL '1 second'
        ORDER BY fecha_creacion DESC
        LIMIT 1
        """,
        (usuario_id, titulo, precio_venta, segundos),
    )
    row = cur.fetchone()
    cur.close()
    release_connection(conn)
    return row["id"] if row else None


def crear_publicacion(data: dict, estado: str = "activa", tier: str = "basico") -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO publicaciones (
            usuario_id, titulo, rubro, provincia, localidad, descripcion,
            precio_venta, facturacion_mensual, resultado_mensual,
            antiguedad_anios, empleados, incluye_inmueble, motivo_venta, estado, tier, es_franquicia
        ) VALUES (%(usuario_id)s, %(titulo)s, %(rubro)s, %(provincia)s, %(localidad)s, %(descripcion)s,
            %(precio_venta)s, %(facturacion_mensual)s, %(resultado_mensual)s,
            %(antiguedad_anios)s, %(empleados)s, %(incluye_inmueble)s, %(motivo_venta)s, %(estado)s, %(tier)s,
            %(es_franquicia)s)
        RETURNING id
        """,
        {"es_franquicia": False, **data, "estado": estado, "tier": tier},
    )
    new_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    release_connection(conn)
    return new_id


def contar_publicaciones_promo_gratis() -> int:
    """Cuántas publicaciones ya usaron el cupo de lanzamiento (primeros N gratis)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM publicaciones WHERE promo_gratis = TRUE")
    total = cur.fetchone()["c"]
    cur.close()
    release_connection(conn)
    return total


def marcar_promo_gratis(pub_id: int, dias: int = 30):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE publicaciones SET promo_gratis = TRUE, "
        "fecha_fin_promo_gratis = NOW() + %s * INTERVAL '1 day' WHERE id = %s",
        (dias, pub_id),
    )
    conn.commit()
    cur.close()
    release_connection(conn)


def publicaciones_promo_vencidas():
    """Publicaciones con el mes de promo gratis vencido que siguen activas (para pausarlas)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.*, u.email, u.nombre FROM publicaciones p
        JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.promo_gratis = TRUE AND p.estado = 'activa' AND p.fecha_fin_promo_gratis < NOW()
        """
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


def activar_publicacion(pub_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE publicaciones SET estado = 'activa' WHERE id = %s", (pub_id,))
    conn.commit()
    cur.close()
    release_connection(conn)


def cambiar_estado_publicacion(pub_id: int, estado: str):
    """estado válido: activa, pausada, vendida"""
    conn = get_connection()
    cur = conn.cursor()
    if estado == "vendida":
        cur.execute("UPDATE publicaciones SET estado = %s, fecha_venta = NOW() WHERE id = %s", (estado, pub_id))
    else:
        cur.execute("UPDATE publicaciones SET estado = %s WHERE id = %s", (estado, pub_id))
    conn.commit()
    cur.close()
    release_connection(conn)


def listar_vendidos_recientes(limite: int = 6):
    """Para prueba social: rubro/ubicación de negocios vendidos, sin exponer precio final ni datos de contacto."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT titulo, rubro, provincia, localidad, fecha_venta
        FROM publicaciones
        WHERE estado = 'vendida'
        ORDER BY fecha_venta DESC NULLS LAST, fecha_creacion DESC
        LIMIT %s
        """,
        (limite,),
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


_SELECT_PUB_CON_CONTACTO = """
    SELECT p.*, u.nombre AS nombre_contacto, u.email AS email_contacto,
           u.telefono AS telefono_contacto
    FROM publicaciones p
    JOIN usuarios u ON u.id = p.usuario_id
"""


def listar_publicaciones(rubro=None, provincia=None, precio_max=None, texto=None, solo_franquicias=False, localidad=None):
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
    if localidad and localidad != "Todas":
        query += " AND p.localidad ILIKE %s"
        params.append(f"%{localidad}%")
    if precio_max:
        query += " AND (p.precio_venta IS NULL OR p.precio_venta <= %s)"
        params.append(precio_max)
    if texto:
        query += " AND (p.titulo ILIKE %s OR p.descripcion ILIKE %s)"
        like = f"%{texto}%"
        params.extend([like, like])
    if solo_franquicias:
        query += " AND p.es_franquicia = TRUE"

    query += " ORDER BY (p.tier = 'destacado') DESC, p.fecha_creacion DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


def obtener_publicacion(pub_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT_PUB_CON_CONTACTO + " WHERE p.id = %s", (pub_id,))
    row = cur.fetchone()
    cur.close()
    release_connection(conn)
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
    release_connection(conn)
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
    release_connection(conn)


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
    release_connection(conn)
    return rows


def contar_consultas_por_publicacion(pub_ids: list):
    """Devuelve {publicacion_id: cantidad_de_consultas} en una sola consulta,
    en vez de una consulta por publicación."""
    if not pub_ids:
        return {}
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT publicacion_id, COUNT(*) AS cantidad
        FROM consultas
        WHERE publicacion_id = ANY(%s)
        GROUP BY publicacion_id
        """,
        (pub_ids,),
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return {r["publicacion_id"]: r["cantidad"] for r in rows}


def marcar_consulta_respondida(consulta_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE consultas SET respondida = TRUE WHERE id = %s", (consulta_id,))
    conn.commit()
    cur.close()
    release_connection(conn)


def agregar_imagen(pub_id: int, url: str, orden: int = 0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO imagenes_publicacion (publicacion_id, url, orden) VALUES (%s, %s, %s)",
        (pub_id, url, orden),
    )
    conn.commit()
    cur.close()
    release_connection(conn)


def agregar_video(pub_id: int, url: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE publicaciones SET video_url = %s WHERE id = %s", (url, pub_id))
    conn.commit()
    cur.close()
    release_connection(conn)


def listar_imagenes(pub_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM imagenes_publicacion WHERE publicacion_id = %s ORDER BY orden, id",
        (pub_id,),
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


def crear_alerta(usuario_id: int, rubro=None, provincia=None, precio_max=None, texto=None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO alertas_busqueda (usuario_id, rubro, provincia, precio_max, texto)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
        """,
        (usuario_id, rubro, provincia, precio_max, texto),
    )
    new_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    release_connection(conn)
    return new_id


def listar_alertas_de_usuario(usuario_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM alertas_busqueda WHERE usuario_id = %s ORDER BY fecha_creacion DESC",
        (usuario_id,),
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


def eliminar_alerta(alerta_id: int, usuario_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM alertas_busqueda WHERE id = %s AND usuario_id = %s",
        (alerta_id, usuario_id),
    )
    conn.commit()
    cur.close()
    release_connection(conn)


def listar_todas_las_alertas():
    """Para el job externo: todas las alertas junto con el email del usuario."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT a.*, u.email, u.nombre
        FROM alertas_busqueda a
        JOIN usuarios u ON u.id = a.usuario_id
        """
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


def publicaciones_nuevas_para_alerta(alerta) -> list:
    conn = get_connection()
    cur = conn.cursor()
    query = _SELECT_PUB_CON_CONTACTO + " WHERE p.estado = 'activa' AND p.fecha_creacion > %s"
    params = [alerta["ultima_revision"]]

    if alerta["rubro"] and alerta["rubro"] != "Todos":
        query += " AND p.rubro = %s"
        params.append(alerta["rubro"])
    if alerta["provincia"] and alerta["provincia"] != "Todas":
        query += " AND p.provincia = %s"
        params.append(alerta["provincia"])
    if alerta["precio_max"]:
        query += " AND (p.precio_venta IS NULL OR p.precio_venta <= %s)"
        params.append(alerta["precio_max"])
    if alerta["texto"]:
        query += " AND (p.titulo ILIKE %s OR p.descripcion ILIKE %s)"
        like = f"%{alerta['texto']}%"
        params.extend([like, like])

    query += " ORDER BY p.fecha_creacion DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


def actualizar_ultima_revision(alerta_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE alertas_busqueda SET ultima_revision = NOW() WHERE id = %s",
        (alerta_id,),
    )
    conn.commit()
    cur.close()
    release_connection(conn)


def es_favorito(usuario_id: int, pub_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM favoritos WHERE usuario_id = %s AND publicacion_id = %s",
        (usuario_id, pub_id),
    )
    row = cur.fetchone()
    cur.close()
    release_connection(conn)
    return row is not None


def agregar_favorito(usuario_id: int, pub_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO favoritos (usuario_id, publicacion_id) VALUES (%s, %s) "
        "ON CONFLICT (usuario_id, publicacion_id) DO NOTHING",
        (usuario_id, pub_id),
    )
    conn.commit()
    cur.close()
    release_connection(conn)


def quitar_favorito(usuario_id: int, pub_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM favoritos WHERE usuario_id = %s AND publicacion_id = %s",
        (usuario_id, pub_id),
    )
    conn.commit()
    cur.close()
    release_connection(conn)


def listar_favoritos_de_usuario(usuario_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        _SELECT_PUB_CON_CONTACTO + """
        JOIN favoritos f ON f.publicacion_id = p.id
        WHERE f.usuario_id = %s
        ORDER BY f.fecha_creacion DESC
        """,
        (usuario_id,),
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


def reporte_precios_por_rubro():
    """Estadísticas agregadas de precio por rubro, para el reporte de precios (contenido de SEO)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            rubro,
            COUNT(*) AS cantidad,
            AVG(precio_venta) AS precio_promedio,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY precio_venta) AS precio_mediana
        FROM publicaciones
        WHERE estado IN ('activa', 'vendida') AND precio_venta IS NOT NULL
        GROUP BY rubro
        ORDER BY cantidad DESC
        """
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
    return rows


def listar_top_precios(limite: int = 10):
    """Ranking de los negocios más caros publicados, para el reporte de precios."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT titulo, rubro, provincia, precio_venta
        FROM publicaciones
        WHERE estado IN ('activa', 'vendida') AND precio_venta IS NOT NULL
        ORDER BY precio_venta DESC
        LIMIT %s
        """,
        (limite,),
    )
    rows = cur.fetchall()
    cur.close()
    release_connection(conn)
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
    release_connection(conn)
    return {r["publicacion_id"]: r["url"] for r in rows}
