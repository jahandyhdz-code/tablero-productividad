"""
database.py — SQLite (local) / PostgreSQL (nube) con interfaz unificada.

Si DATABASE_URL está definida en el entorno se usa PostgreSQL.
Si no, usa SQLite local (ventas.db) para desarrollo.
"""
import json
import os
import calendar
from datetime import date, datetime, timedelta
from contextlib import contextmanager
from pathlib import Path

# ── Detectar modo de base de datos ──────────────────────────────────────────
_DATABASE_URL = os.environ.get("DATABASE_URL", "")
_USE_PG = bool(_DATABASE_URL)

if _USE_PG:
    import psycopg2
    import psycopg2.extras
else:
    import sqlite3
    _DB_PATH = Path(__file__).parent / "ventas.db"

# ────────────────────────────────────────────────────────────────────────────
#  CATÁLOGOS
# ────────────────────────────────────────────────────────────────────────────

DETERMINANTES = sorted([
    "1° de Mayo", "16 de Septiembre", "Acambay", "Acolman", "Aculco",
    "Almoloya", "Alpinismo", "Amecameca", "Angeles Iztapalapa", "Apaxco",
    "Arca de Noé", "Arbolada los Sauces", "Atana", "Atlacomulco", "Aurora",
    "Autopista Querétaro", "Av. Central", "Av. Nacional", "Avenida Dalias",
    "Ayotla", "Azcapotzalco", "Bolivar", "Bosques de Tecámac",
    "Bosques del Valle", "Bulevares del Lago", "Cabeza de Juarez",
    "Camino Recursos Hidraulicos", "Cantil", "Capultitlan", "Cd Labor",
    "Centenario", "Chalco 2000", "Chicoloapan",
    "Chimalhuácan Mariano Escobedo", "Chimalhuácan Peñón", "Chinampa",
    "Citara- Huehuetoca", "Coatepec Harinas", "Cofradías",
    "Colina de Monte Bello", "Cristóbal", "Cuauhtémoc", "Cuautitlán",
    "Cuautzingo", "Dimas", "Doctores", "Ecatepec", "El Dorado", "El Oro",
    "El Oro de Hidalgo", "El Tenayo", "Etzatlán", "Ferrocarril Hidalgo",
    "Flores Magón", "Fuentes del Valle", "Gobernadora", "Guadalupana",
    "Héroes Tecámac", "Huehuetoca", "Insurgentes Norte", "Insurgentes Sur",
    "Ixtapaluca", "Ixtlahuaca", "Iztapalapa", "Iztapalapa Norte",
    "Jesus Chaparro", "Jilotepec", "Jocotitlán", "Joyas de Coacalco",
    "Juchitepec", "La Aurora", "La Crespa", "La Palma", "La Paz",
    "La Presa", "La Viga", "La Villa", "La Virgen", "Lindavista",
    "Lomas Estrella", "Los Reyes", "Mariano Escobedo", "Melchor Ocampo",
    "Mexiquense", "Molina Enriquez", "Nextlalpan", "Nicolás Bravo",
    "Nicolás Romero", "Observatorio", "Ocoyoacac", "Otumba", "Ozumba",
    "Palomas", "Pantitlán", "Paseo del Rey", "Pensador Mexicano",
    "Plaza Aragón", "Plaza Atizapán", "Plaza Chimalhuácan",
    "Plaza Churubusco", "Plaza Cuautitlán", "Plaza Ecatepec",
    "Portal Chalco", "Rancho San Juan", "Real de Costitlan", "Rio Hondo",
    "San Agustin Ecatepec", "San Andres Cuexcontitlan", "San Buenaventura",
    "San Juan de Aragón", "San Juan de la Labor", "San Juanico",
    "San Lorenzo", "San Mateo Atenco", "San Mateo Atarasquillo",
    "San Mateo Nopala", "San Pablo Autopan", "San Pablo Tultitlán",
    "San Rafael", "Santa Cecilia", "Santa Clara", "Santa Cruz",
    "Santa Cruz Atizapán", "Santa Fe", "Santa Inés", "Santa Lucia",
    "Santiago", "Santiaguito", "Sor Juana", "Tacubaya", "Tecalco",
    "Tecámac", "Tejupilco", "Temoaya", "Tenancingo", "Tenango", "Teneria",
    "Teotihuácan", "Tepojaco", "Tepotztitlán", "Tequixquiac", "Terranova",
    "Texcoco", "Tianguistenco", "Tlalcilalcalpan", "Tlalmanalco",
    "Tlalnepantla", "Toluca Aztecas", "Toluca Pilares", "Totoltepec",
    "Tulyehualco", "Valle de Aragón", "Valle de Chalco", "Vallejo",
    "Vía Morelos", "Viento Nuevo", "Villa Coapa", "Villa del Carbon",
    "Villa Guerrero", "Villa Victoria", "Villa Victoria Sur",
    "Villas de Ayotla", "Villas de la Hacienda", "Xalostoc", "Xochimilco",
    "Xonacatlán", "Zaragoza", "Zinacantepec", "Zumpango",
], key=str.casefold)

MONTHS_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]

DAILY_GOAL: float = 6.0


# ────────────────────────────────────────────────────────────────────────────
#  CONEXIÓN UNIFICADA
# ────────────────────────────────────────────────────────────────────────────

@contextmanager
def get_conn():
    if _USE_PG:
        conn = psycopg2.connect(_DATABASE_URL)
        conn.autocommit = False
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(_DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def _exec(conn, sql: str, params=()) -> "cursor":
    """Ejecuta SQL normalizando placeholders según el driver activo."""
    if _USE_PG:
        # psycopg2 usa %s en lugar de ?
        sql = sql.replace("?", "%s")
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = conn.cursor()
    cur.execute(sql, params)
    return cur


def _fetchall(cur) -> list[dict]:
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def _fetchone(cur):
    row = cur.fetchone()
    return dict(row) if row else None


# ────────────────────────────────────────────────────────────────────────────
#  INIT & MIGRATIONS
# ────────────────────────────────────────────────────────────────────────────

def init_db():
    with get_conn() as conn:
        if _USE_PG:
            _pg_init(conn)
        else:
            _sqlite_init(conn)


def _sqlite_init(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        associate_number     TEXT    UNIQUE NOT NULL,
        name                 TEXT    NOT NULL,
        password_hash        TEXT    NOT NULL,
        role                 TEXT    NOT NULL DEFAULT 'user',
        tienda               TEXT    NOT NULL DEFAULT '',
        must_change_password INTEGER NOT NULL DEFAULT 1,
        admin_tiendas        TEXT    DEFAULT NULL,
        created_at           TEXT    NOT NULL DEFAULT (datetime('now')),
        determinante         TEXT    NOT NULL DEFAULT '',
        squad                TEXT    NOT NULL DEFAULT '',
        distrito             TEXT    NOT NULL DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS sales_targets (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL REFERENCES users(id),
        year         INTEGER NOT NULL,
        month        INTEGER NOT NULL,
        target_units REAL    NOT NULL,
        UNIQUE (user_id, year, month)
    );
    CREATE TABLE IF NOT EXISTS sales_entries (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id         INTEGER NOT NULL REFERENCES users(id),
        entry_date      TEXT    NOT NULL,
        units_sold      REAL    NOT NULL,
        units_gana_plus REAL    NOT NULL DEFAULT 0,
        units_kiosko    REAL    NOT NULL DEFAULT 0,
        notes           TEXT,
        created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS sessions (
        token      TEXT    PRIMARY KEY,
        user_id    INTEGER NOT NULL REFERENCES users(id),
        expires_at TEXT    NOT NULL
    );
    CREATE TABLE IF NOT EXISTS rest_days (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id   INTEGER NOT NULL REFERENCES users(id),
        rest_date TEXT    NOT NULL,
        UNIQUE (user_id, rest_date)
    );
    CREATE TABLE IF NOT EXISTS pets (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id       INTEGER NOT NULL UNIQUE REFERENCES users(id),
        animal_type   TEXT    NOT NULL,
        pet_name      TEXT    NOT NULL DEFAULT 'Mi Mascota',
        stage         TEXT    NOT NULL DEFAULT 'huevo',
        coins         INTEGER NOT NULL DEFAULT 0,
        xp            INTEGER NOT NULL DEFAULT 0,
        hunger        INTEGER NOT NULL DEFAULT 100,
        happiness     INTEGER NOT NULL DEFAULT 100,
        last_activity TEXT    NOT NULL DEFAULT (datetime('now')),
        created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS pet_items (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id       INTEGER NOT NULL REFERENCES pets(id),
        item_type    TEXT    NOT NULL,
        equipped     INTEGER NOT NULL DEFAULT 0,
        purchased_at TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS pet_actions_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id      INTEGER NOT NULL REFERENCES pets(id),
        action      TEXT    NOT NULL,
        detail      TEXT,
        coins_delta INTEGER NOT NULL DEFAULT 0,
        xp_delta    INTEGER NOT NULL DEFAULT 0,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS game_plays (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL REFERENCES users(id),
        game_type  TEXT    NOT NULL,
        played_at  TEXT    NOT NULL DEFAULT (datetime('now')),
        coins_won  INTEGER NOT NULL DEFAULT 0,
        xp_won     INTEGER NOT NULL DEFAULT 0,
        result     TEXT
    );
    CREATE TABLE IF NOT EXISTS store_budgets (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        determinante TEXT   NOT NULL DEFAULT '',
        tienda      TEXT    NOT NULL,
        year        INTEGER NOT NULL,
        month       INTEGER NOT NULL,
        presupuesto REAL    NOT NULL,
        UNIQUE (determinante, year, month)
    );
    CREATE TABLE IF NOT EXISTS store_daily_budgets (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        determinante TEXT   NOT NULL,
        year        INTEGER NOT NULL,
        month       INTEGER NOT NULL,
        day         INTEGER NOT NULL,
        presupuesto REAL    NOT NULL,
        UNIQUE (determinante, year, month, day)
    );
    """)


def _pg_init(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id                   SERIAL PRIMARY KEY,
        associate_number     TEXT   UNIQUE NOT NULL,
        name                 TEXT   NOT NULL,
        password_hash        TEXT   NOT NULL,
        role                 TEXT   NOT NULL DEFAULT 'user',
        tienda               TEXT   NOT NULL DEFAULT '',
        must_change_password INTEGER NOT NULL DEFAULT 1,
        admin_tiendas      TEXT   DEFAULT NULL,
        created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        determinante         TEXT   NOT NULL DEFAULT '',
        squad                TEXT   NOT NULL DEFAULT '',
        distrito             TEXT   NOT NULL DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS sales_targets (
        id           SERIAL PRIMARY KEY,
        user_id      INTEGER NOT NULL REFERENCES users(id),
        year         INTEGER NOT NULL,
        month        INTEGER NOT NULL,
        target_units REAL    NOT NULL,
        UNIQUE (user_id, year, month)
    );
    CREATE TABLE IF NOT EXISTS sales_entries (
        id              SERIAL PRIMARY KEY,
        user_id         INTEGER NOT NULL REFERENCES users(id),
        entry_date      DATE    NOT NULL,
        units_sold      REAL    NOT NULL,
        units_gana_plus REAL    NOT NULL DEFAULT 0,
        units_kiosko    REAL    NOT NULL DEFAULT 0,
        notes           TEXT,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS sessions (
        token      TEXT PRIMARY KEY,
        user_id    INTEGER NOT NULL REFERENCES users(id),
        expires_at TIMESTAMPTZ NOT NULL
    );
    CREATE TABLE IF NOT EXISTS rest_days (
        id        SERIAL PRIMARY KEY,
        user_id   INTEGER NOT NULL REFERENCES users(id),
        rest_date DATE    NOT NULL,
        UNIQUE (user_id, rest_date)
    );
    CREATE TABLE IF NOT EXISTS pets (
        id            SERIAL PRIMARY KEY,
        user_id       INTEGER NOT NULL UNIQUE REFERENCES users(id),
        animal_type   TEXT    NOT NULL,
        pet_name      TEXT    NOT NULL DEFAULT 'Mi Mascota',
        stage         TEXT    NOT NULL DEFAULT 'huevo',
        coins         INTEGER NOT NULL DEFAULT 0,
        xp            INTEGER NOT NULL DEFAULT 0,
        hunger        INTEGER NOT NULL DEFAULT 100,
        happiness     INTEGER NOT NULL DEFAULT 100,
        last_activity TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS pet_items (
        id           SERIAL PRIMARY KEY,
        pet_id       INTEGER NOT NULL REFERENCES pets(id),
        item_type    TEXT    NOT NULL,
        equipped     INTEGER NOT NULL DEFAULT 0,
        purchased_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS pet_actions_log (
        id          SERIAL PRIMARY KEY,
        pet_id      INTEGER NOT NULL REFERENCES pets(id),
        action      TEXT    NOT NULL,
        detail      TEXT,
        coins_delta INTEGER NOT NULL DEFAULT 0,
        xp_delta    INTEGER NOT NULL DEFAULT 0,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS game_plays (
        id         SERIAL PRIMARY KEY,
        user_id    INTEGER NOT NULL REFERENCES users(id),
        game_type  TEXT    NOT NULL,
        played_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        coins_won  INTEGER NOT NULL DEFAULT 0,
        xp_won     INTEGER NOT NULL DEFAULT 0,
        result     TEXT
    );
    CREATE TABLE IF NOT EXISTS user_meta (
        id          SERIAL PRIMARY KEY,
        user_id     INTEGER NOT NULL REFERENCES users(id),
        year        INTEGER NOT NULL,
        month       INTEGER NOT NULL,
        meta_tienda REAL    NOT NULL DEFAULT 0,
        plantilla   INTEGER NOT NULL DEFAULT 1,
        UNIQUE(user_id, year, month)
    );
    """)


def _add_col_if_missing(table: str, col: str, col_def: str):
    """Safe ALTER TABLE — idempotente en SQLite y PostgreSQL."""
    with get_conn() as conn:
        if _USE_PG:
            cur = conn.cursor()
            cur.execute("""
                SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s
            """, (table, col))
            if not cur.fetchone():
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
        else:
            cols = [r[1] for r in conn.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()]
            if col not in cols:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")


def run_migrations():
    """Migraciones idempotentes."""
    _add_col_if_missing("users", "tienda",               "TEXT NOT NULL DEFAULT ''")
    _add_col_if_missing("users", "must_change_password",  "INTEGER NOT NULL DEFAULT 0")
    _add_col_if_missing("users", "admin_tiendas",         "TEXT DEFAULT NULL")
    _add_col_if_missing("users", "determinante",          "TEXT NOT NULL DEFAULT ''")
    _add_col_if_missing("users", "squad",                 "TEXT NOT NULL DEFAULT ''")
    _add_col_if_missing("users", "distrito",              "TEXT NOT NULL DEFAULT ''")
    _add_col_if_missing("sales_entries", "units_gana_plus",  "REAL NOT NULL DEFAULT 0")
    _add_col_if_missing("sales_entries", "units_kiosko",     "REAL NOT NULL DEFAULT 0")
    _add_col_if_missing("sales_entries", "order_number",     "TEXT")
    _add_col_if_missing("sales_entries", "status",           "TEXT NOT NULL DEFAULT 'pendiente'")
    _add_col_if_missing("sales_entries", "amount_sin_iva",   "REAL NOT NULL DEFAULT 0")
    _add_col_if_missing("sales_entries", "almacen",          "TEXT")
    _add_col_if_missing("sales_entries", "descripcion",      "TEXT")
    # game_plays se crea en init_db; migracion por si la tabla ya existia sin columnas
    _add_col_if_missing("game_plays",    "xp_won",           "INTEGER NOT NULL DEFAULT 0")
    _add_col_if_missing("game_plays",    "result",           "TEXT")
    # Tamagotchi 2.0 — hambre con decaimiento temporal
    _add_col_if_missing("pets", "hunger_updated_at",
                        "TIMESTAMPTZ NOT NULL DEFAULT NOW()" if _USE_PG
                        else "TEXT NOT NULL DEFAULT (datetime('now'))")
    # Presupuestos por tienda (carga masiva via Excel)
    with get_conn() as conn:
        if _USE_PG:
            conn.cursor().execute("""
                CREATE TABLE IF NOT EXISTS store_budgets (
                    id          SERIAL PRIMARY KEY,
                    determinante TEXT NOT NULL DEFAULT '',
                    tienda      TEXT    NOT NULL,
                    year        INTEGER NOT NULL,
                    month       INTEGER NOT NULL,
                    presupuesto REAL    NOT NULL,
                    UNIQUE (determinante, year, month)
                )""")
            conn.cursor().execute("""
                CREATE TABLE IF NOT EXISTS store_daily_budgets (
                    id          SERIAL PRIMARY KEY,
                    determinante TEXT NOT NULL,
                    year        INTEGER NOT NULL,
                    month       INTEGER NOT NULL,
                    day         INTEGER NOT NULL,
                    presupuesto REAL    NOT NULL,
                    UNIQUE (determinante, year, month, day)
                )""")
        else:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS store_budgets (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    determinante TEXT NOT NULL DEFAULT '',
                    tienda      TEXT    NOT NULL,
                    year        INTEGER NOT NULL,
                    month       INTEGER NOT NULL,
                    presupuesto REAL    NOT NULL,
                    UNIQUE (determinante, year, month)
                )""")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS store_daily_budgets (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    determinante TEXT NOT NULL,
                    year        INTEGER NOT NULL,
                    month       INTEGER NOT NULL,
                    day         INTEGER NOT NULL,
                    presupuesto REAL    NOT NULL,
                    UNIQUE (determinante, year, month, day)
                )""")
    # Columna determinante en users (para ligar al asesor con su tienda)
    _add_col_if_missing("users", "determinante", "TEXT NOT NULL DEFAULT ''")
    # Columna determinante en store_budgets (puede existir sin ella en DBs viejas)
    _add_col_if_missing("store_budgets", "determinante", "TEXT NOT NULL DEFAULT ''")


# ────────────────────────────────────────────────────────────────────────────
#  DATE HELPERS (SQLite usa strftime, PG usa TO_CHAR)
# ────────────────────────────────────────────────────────────────────────────

def _year_filter(col: str) -> str:
    if _USE_PG:
        return f"TO_CHAR({col}, 'YYYY') = %s"
    return f"strftime('%Y', {col}) = ?"


def _month_filter(col: str) -> str:
    if _USE_PG:
        return f"TO_CHAR({col}, 'MM') = %s"
    return f"strftime('%m', {col}) = ?"


# ────────────────────────────────────────────────────────────────────────────
#  USERS
# ────────────────────────────────────────────────────────────────────────────

def create_user(associate_number: str, name: str, password_hash: str,
                role: str = "user", tienda: str = "",
                must_change_password: int = 1) -> int:
    """must_change_password=1 para admin-creados, 0 para auto-registro."""
    with get_conn() as conn:
        if _USE_PG:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO users
                   (associate_number, name, password_hash, role, tienda, must_change_password)
                   VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
                (associate_number.strip(), name.strip(), password_hash, role,
                 tienda.strip(), must_change_password),
            )
            return cur.fetchone()[0]
        else:
            cur = conn.execute(
                """INSERT INTO users
                   (associate_number, name, password_hash, role, tienda, must_change_password)
                   VALUES (?,?,?,?,?,?)""",
                (associate_number.strip(), name.strip(), password_hash, role,
                 tienda.strip(), must_change_password),
            )
            return cur.lastrowid


def get_user_by_associate(associate_number: str):
    with get_conn() as conn:
        cur = _exec(conn, "SELECT * FROM users WHERE associate_number = ?",
                    (associate_number.strip(),))
        return _fetchone(cur)


def get_user_by_id(user_id: int):
    with get_conn() as conn:
        cur = _exec(conn, "SELECT * FROM users WHERE id = ?", (user_id,))
        return _fetchone(cur)


def get_all_users(tiendas_filter: list | None = None) -> list[dict]:
    with get_conn() as conn:
        if tiendas_filter:
            ph = ",".join(["%s" if _USE_PG else "?"] * len(tiendas_filter))
            cur = _exec(
                conn,
                f"SELECT id,associate_number,name,role,tienda,determinante,"
                f"squad,distrito,admin_tiendas,created_at"
                f" FROM users WHERE tienda IN ({ph}) ORDER BY name",
                tiendas_filter,
            )
        else:
            cur = _exec(
                conn,
                "SELECT id,associate_number,name,role,tienda,determinante,"
                "squad,distrito,admin_tiendas,created_at"
                " FROM users ORDER BY name",
            )
        return _fetchall(cur)


def get_admin_tiendas(user_id: int) -> list[str]:
    with get_conn() as conn:
        cur = _exec(conn, "SELECT admin_tiendas FROM users WHERE id=?", (user_id,))
        row = _fetchone(cur)
    if not row or not row.get("admin_tiendas"):
        return []
    return json.loads(row["admin_tiendas"])


def set_admin_tiendas(user_id: int, tiendas: list[str]) -> None:
    val = json.dumps(sorted(tiendas), ensure_ascii=False) if tiendas else None
    with get_conn() as conn:
        _exec(conn, "UPDATE users SET admin_tiendas=? WHERE id=?", (val, user_id))


def update_user_password(user_id: int, password_hash: str, clear_force: bool = False):
    with get_conn() as conn:
        if clear_force:
            _exec(conn,
                  "UPDATE users SET password_hash=?, must_change_password=0 WHERE id=?",
                  (password_hash, user_id))
        else:
            _exec(conn, "UPDATE users SET password_hash=? WHERE id=?",
                  (password_hash, user_id))


def update_user_determinante(user_id: int, determinante: str):
    """Guarda el determinante de tienda del usuario."""
    ph = "%s" if _USE_PG else "?"
    with get_conn() as conn:
        _exec(conn,
              f"UPDATE users SET determinante={ph} WHERE id={ph}",
              (determinante, user_id))


def update_user_squad_distrito(user_id: int, squad: str, distrito: str):
    """Guarda squad y distrito del usuario."""
    ph = "%s" if _USE_PG else "?"
    with get_conn() as conn:
        _exec(conn,
              f"UPDATE users SET squad={ph}, distrito={ph} WHERE id={ph}",
              (squad.strip(), distrito.strip(), user_id))


def associate_number_exists(associate_number: str) -> bool:
    with get_conn() as conn:
        cur = _exec(conn,
                    "SELECT 1 FROM users WHERE associate_number = ?",
                    (associate_number.strip(),))
        return _fetchone(cur) is not None


def delete_user(user_id: int) -> None:
    with get_conn() as conn:
        # Tablas que apuntan a pets por FK pet_id
        _exec(conn, """
            DELETE FROM pet_items WHERE pet_id IN
            (SELECT id FROM pets WHERE user_id = ?)""", (user_id,))
        _exec(conn, """
            DELETE FROM pet_actions_log WHERE pet_id IN
            (SELECT id FROM pets WHERE user_id = ?)""", (user_id,))
        # Tablas con FK directo a user_id
        _exec(conn, "DELETE FROM pets          WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM user_meta     WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM game_plays    WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM orders        WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM sessions      WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM rest_days     WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM sales_entries WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM sales_targets WHERE user_id = ?", (user_id,))
        # Por ultimo el usuario
        _exec(conn, "DELETE FROM users         WHERE id      = ?", (user_id,))


# ────────────────────────────────────────────────────────────────────────────
#  SESSIONS
# ────────────────────────────────────────────────────────────────────────────

def create_session(token: str, user_id: int, hours: int = 8):
    expires = (datetime.utcnow() + timedelta(hours=hours)).isoformat()
    with get_conn() as conn:
        _exec(conn,
              "INSERT INTO sessions (token, user_id, expires_at) VALUES (?,?,?)",
              (token, user_id, expires))


def get_session(token: str):
    with get_conn() as conn:
        cur = _exec(conn, "SELECT * FROM sessions WHERE token = ?", (token,))
        row = _fetchone(cur)
    if not row:
        return None
    exp = row["expires_at"]
    if isinstance(exp, str):
        exp = datetime.fromisoformat(exp)
    else:
        exp = exp.replace(tzinfo=None)   # PG devuelve datetime aware
    if exp < datetime.utcnow():
        delete_session(token)
        return None
    return row


def delete_session(token: str):
    with get_conn() as conn:
        _exec(conn, "DELETE FROM sessions WHERE token = ?", (token,))


# ────────────────────────────────────────────────────────────────────────────
#  SALES TARGETS
# ────────────────────────────────────────────────────────────────────────────

def set_sales_target(user_id: int, year: int, month: int, target_units: float):
    with get_conn() as conn:
        if _USE_PG:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO sales_targets (user_id, year, month, target_units)
                VALUES (%s,%s,%s,%s)
                ON CONFLICT (user_id, year, month)
                DO UPDATE SET target_units = EXCLUDED.target_units
            """, (user_id, year, month, target_units))
        else:
            conn.execute("""
                INSERT INTO sales_targets (user_id, year, month, target_units)
                VALUES (?,?,?,?)
                ON CONFLICT(user_id, year, month)
                DO UPDATE SET target_units = excluded.target_units
            """, (user_id, year, month, target_units))


def get_sales_target(user_id: int, year: int, month: int) -> float | None:
    with get_conn() as conn:
        cur = _exec(conn,
                    "SELECT target_units FROM sales_targets"
                    " WHERE user_id=? AND year=? AND month=?",
                    (user_id, year, month))
        row = _fetchone(cur)
    return float(row["target_units"]) if row else None


# ────────────────────────────────────────────────────────────────────────────
#  META MENSUAL + PLANTILLA
# ────────────────────────────────────────────────────────────────────────────

def _init_user_meta_table(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_meta (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            year        INTEGER NOT NULL,
            month       INTEGER NOT NULL,
            meta_tienda REAL    NOT NULL DEFAULT 0,
            plantilla   INTEGER NOT NULL DEFAULT 1,
            UNIQUE(user_id, year, month)
        )
    """)
    conn.commit()


if not _USE_PG:
    with get_conn() as conn:
        _init_user_meta_table(conn)


def get_user_meta(user_id: int, year: int, month: int) -> dict | None:
    """Retorna meta_tienda y plantilla del usuario para el mes dado."""
    with get_conn() as conn:
        cur = _exec(conn,
                    "SELECT meta_tienda, plantilla FROM user_meta"
                    " WHERE user_id=? AND year=? AND month=?",
                    (user_id, year, month))
        return _fetchone(cur)


def set_user_meta(user_id: int, year: int, month: int,
                  meta_tienda: float, plantilla: int) -> float:
    """
    Guarda meta_tienda y plantilla.
    Deriva y guarda target individual = meta_tienda / plantilla.
    Retorna el objetivo individual calculado.
    """
    plantilla  = max(plantilla, 1)  # evitar division por cero
    individual = round(meta_tienda / plantilla, 1)

    with get_conn() as conn:
        _exec(conn, """
            INSERT INTO user_meta (user_id, year, month, meta_tienda, plantilla)
            VALUES (?,?,?,?,?)
            ON CONFLICT(user_id, year, month)
            DO UPDATE SET meta_tienda=excluded.meta_tienda,
                          plantilla=excluded.plantilla
        """, (user_id, year, month, meta_tienda, plantilla))

    # Actualiza el target individual en sales_targets
    set_sales_target(user_id, year, month, individual)
    return individual
# ────────────────────────────────────────────────────────────────────────────

def toggle_rest_day(user_id: int, rest_date: str) -> bool:
    with get_conn() as conn:
        cur = _exec(conn,
                    "SELECT 1 FROM rest_days WHERE user_id=? AND rest_date=?",
                    (user_id, rest_date))
        if _fetchone(cur):
            _exec(conn,
                  "DELETE FROM rest_days WHERE user_id=? AND rest_date=?",
                  (user_id, rest_date))
            return False
        _exec(conn,
              "INSERT INTO rest_days (user_id, rest_date) VALUES (?,?)",
              (user_id, rest_date))
        return True


def get_rest_days_for_month(user_id: int, year: int, month: int) -> set:
    yf = _year_filter("rest_date")
    mf = _month_filter("rest_date")
    with get_conn() as conn:
        cur = _exec(conn,
                    f"SELECT rest_date FROM rest_days WHERE user_id=? AND {yf} AND {mf}",
                    (user_id, str(year), f"{month:02d}"))
        rows = _fetchall(cur)
    return {str(r["rest_date"]) for r in rows}


# ────────────────────────────────────────────────────────────────────────────
#  SALES ENTRIES
# ────────────────────────────────────────────────────────────────────────────

# Longitudes validas para numero de pedido
ORDER_NUMBER_LENGTHS = (13, 15)


def validate_order_number(order_number: str) -> tuple[bool, str]:
    """
    Valida que el numero de pedido sea solo digitos y tenga 13 o 15 caracteres.
    Retorna (ok, mensaje_error).
    """
    num = order_number.strip()
    if not num.isdigit():
        return False, "El numero de pedido solo debe contener digitos."
    if len(num) not in ORDER_NUMBER_LENGTHS:
        return False, f"El numero de pedido debe tener 13 o 15 digitos (tiene {len(num)})."
    return True, ""


def get_order_number_owner(order_number: str) -> dict | None:
    """
    Busca si el numero de pedido ya existe en sales_entries.
    Retorna dict con name y associate_number del dueno, o None si no existe.
    """
    with get_conn() as conn:
        cur = _exec(conn,
                    """SELECT u.name, u.associate_number
                       FROM sales_entries s
                       JOIN users u ON s.user_id = u.id
                       WHERE s.order_number = ?
                       LIMIT 1""",
                    (order_number.strip(),))
        return _fetchone(cur)


def add_sales_entry(user_id: int, entry_date: str, units_sold: float,
                    gana_plus: float = 0.0, kiosko: float = 0.0,
                    order_number: str = "",
                    amount_sin_iva: float = 0.0,
                    almacen: str = "",
                    descripcion: str = "") -> int:
    num  = order_number.strip() or None
    alm  = almacen.strip() or None
    desc = descripcion.strip() or None
    with get_conn() as conn:
        if _USE_PG:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO sales_entries
                (user_id, entry_date, units_sold, units_gana_plus, units_kiosko,
                 order_number, status, amount_sin_iva, almacen, descripcion)
                VALUES (%s,%s,%s,%s,%s,%s,'pendiente',%s,%s,%s) RETURNING id
            """, (user_id, entry_date, units_sold, gana_plus, kiosko, num, amount_sin_iva, alm, desc))
            return cur.fetchone()[0]
        else:
            cur = conn.execute("""
                INSERT INTO sales_entries
                (user_id, entry_date, units_sold, units_gana_plus, units_kiosko,
                 order_number, status, amount_sin_iva, almacen, descripcion)
                VALUES (?,?,?,?,?,?,'pendiente',?,?,?)
            """, (user_id, entry_date, units_sold, gana_plus, kiosko, num, amount_sin_iva, alm, desc))
            return cur.lastrowid


def delete_sales_entry(entry_id: int, user_id: int) -> bool:
    with get_conn() as conn:
        cur = _exec(conn,
                    "DELETE FROM sales_entries WHERE id=? AND user_id=?",
                    (entry_id, user_id))
        return cur.rowcount > 0


def get_sales_for_month(user_id: int, year: int, month: int):
    yf = _year_filter("entry_date")
    mf = _month_filter("entry_date")
    with get_conn() as conn:
        cur = _exec(conn,
                    f"""SELECT id, entry_date, units_sold,
                               units_gana_plus, units_kiosko, created_at, order_number
                        FROM sales_entries
                        WHERE user_id=? AND {yf} AND {mf} {_EXCL}
                        ORDER BY entry_date DESC, id DESC""",
                    (user_id, str(year), f"{month:02d}"))
        rows = _fetchall(cur)
    # Normalizar entry_date a string
    for r in rows:
        r["entry_date"] = str(r["entry_date"])
    return rows


def get_sales_for_week(user_id: int, week_start: date, week_end: date) -> float:
    with get_conn() as conn:
        cur = _exec(conn,
                    f"""SELECT COALESCE(SUM(units_sold),0) as total FROM sales_entries
                       WHERE user_id=? AND entry_date>=? AND entry_date<=? {_EXCL}""",
                    (user_id, week_start.isoformat(), week_end.isoformat()))
        row = _fetchone(cur)
    return float(row["total"]) if row else 0.0


def get_sales_for_day(user_id: int, day: date) -> float:
    with get_conn() as conn:
        cur = _exec(conn,
                    f"""SELECT COALESCE(SUM(units_sold),0) as total FROM sales_entries
                       WHERE user_id=? AND entry_date=? {_EXCL}""",
                    (user_id, day.isoformat()))
        row = _fetchone(cur)
    return float(row["total"]) if row else 0.0


# Estatus excluidos de TODOS los conteos y sumas de ventas
_EXCL = "AND COALESCE(status,'pendiente') NOT IN ('cancelado','devolucion')"

def _pct(actual: float, target: float) -> float:
    if not target:
        return 0.0
    return round((actual / target) * 100, 1)


def commercial_week(ref: date) -> tuple[date, date]:
    """Semana comercial Walmart: Sábado a Viernes."""
    days_since_sat = (ref.weekday() - 5) % 7
    week_start = ref - timedelta(days=days_since_sat)
    week_end   = week_start + timedelta(days=6)
    return week_start, week_end


# Meta fija de pedidos por día laborable
_PEDIDOS_POR_DIA = 6


def get_productivity_metrics(user_id: int, year: int, month: int) -> dict:
    today = date.today()
    days_in_month  = calendar.monthrange(year, month)[1]

    rest_days = get_rest_days_for_month(user_id, year, month)
    working_days_month = max(days_in_month - len(rest_days), 1)

    # Meta de PEDIDOS: 6 fijos por día laborable
    today_is_rest = today.isoformat() in rest_days
    today_target  = 0 if today_is_rest else _PEDIDOS_POR_DIA

    week_start, week_end = commercial_week(today)
    working_days_week = sum(
        1 for i in range(7)
        if (week_start + timedelta(days=i)).month == month
        and (week_start + timedelta(days=i)).isoformat() not in rest_days
    )
    weekly_target  = working_days_week * _PEDIDOS_POR_DIA
    monthly_target = working_days_month * _PEDIDOS_POR_DIA

    monthly_entries = get_sales_for_month(user_id, year, month)
    monthly_actual  = sum(e["units_sold"] for e in monthly_entries)
    weekly_actual   = get_sales_for_week(user_id, week_start, week_end)
    daily_actual    = get_sales_for_day(user_id, today)
    daily_diff      = round(daily_actual - today_target, 1)

    # Productividad diaria: pedidos del mes / dias laborados hasta hoy
    first_of_month = date(year, month, 1)
    if year == today.year and month == today.month:
        last_elapsed = today
    else:
        last_elapsed = date(year, month, days_in_month)
    elapsed_days    = (last_elapsed - first_of_month).days + 1
    rest_in_elapsed = sum(1 for d in rest_days if d <= last_elapsed.isoformat())
    dias_laborados  = max(elapsed_days - rest_in_elapsed, 1)
    prod_diaria     = round(monthly_actual / dias_laborados, 1)

    daily_map: dict[str, float] = {}
    for e in monthly_entries:
        d = str(e["entry_date"])
        daily_map[d] = daily_map.get(d, 0.0) + e["units_sold"]

    chart_labels = list(range(1, days_in_month + 1))
    chart_data   = [daily_map.get(date(year, month, d).isoformat(), 0.0) for d in chart_labels]
    chart_rest   = [date(year, month, d).isoformat() in rest_days for d in chart_labels]

    return {
        "daily":   {"actual": daily_actual,   "target": today_target,
                    "pct": _pct(daily_actual, today_target), "diff": daily_diff},
        "weekly":  {"actual": weekly_actual,  "target": weekly_target,
                    "pct": _pct(weekly_actual, weekly_target)},
        "monthly": {"actual": monthly_actual, "target": monthly_target,
                    "pct": _pct(monthly_actual, monthly_target)},
        "prod_diaria":    prod_diaria,
        "dias_laborados": dias_laborados,
        "chart_labels":  chart_labels,
        "chart_data":    chart_data,
        "chart_rest":    chart_rest,
        "rest_days":     rest_days,
        "first_weekday": date(year, month, 1).weekday(),
        "entries":       monthly_entries,
        "today":         today.isoformat(),
        "has_target":    True,  # Siempre hay meta: 6 pedidos/dia laborable
        "daily_target":  _PEDIDOS_POR_DIA,
    }


def get_team_productivity(year: int, month: int,
                          tiendas_filter: list | None = None) -> list[dict]:
    today      = date.today()
    first_day  = date(year, month, 1)
    days_in_month = calendar.monthrange(year, month)[1]

    # Ultimo dia considerado: hoy si es el mes en curso, o fin de mes si es pasado
    if year == today.year and month == today.month:
        last_elapsed = today
    else:
        last_elapsed = date(year, month, days_in_month)

    result = []
    for u in get_all_users(tiendas_filter=tiendas_filter):
        monthly_target = get_sales_target(u["id"], year, month) or 0.0
        entries        = get_sales_for_month(u["id"], year, month)
        monthly_actual = sum(e["units_sold"] for e in entries)

        rest_set = get_rest_days_for_month(u["id"], year, month)

        # Dias laborados = dias transcurridos - descansos en ese periodo
        elapsed_days    = (last_elapsed - first_day).days + 1
        rest_in_elapsed = sum(1 for d in rest_set if d <= last_elapsed.isoformat())
        dias_laborados  = max(elapsed_days - rest_in_elapsed, 1)

        # Nueva formula de productividad
        prod_mensual    = round(monthly_actual / dias_laborados, 1)
        daily_from_month = monthly_target / max(days_in_month - len(rest_set), 1) if monthly_target else 0.0

        today_actual = get_sales_for_day(u["id"], today)

        # Desglose dia a dia de todo el mes (hasta hoy si es el mes en curso)
        month_days = []
        for i in range((last_elapsed - first_day).days + 1):
            d = first_day + timedelta(days=i)
            day_sales = get_sales_for_day(u["id"], d)
            month_days.append({
                "date":     d.isoformat(),
                "label":    ["Lun","Mar","Mie","Jue","Vie","Sab","Dom"][d.weekday()],
                "day":      d.day,
                "units":    day_sales,
                "is_today": d == today,
                "is_rest":  d.isoformat() in rest_set,
            })

        result.append({
            **u,
            "monthly_target":   monthly_target,
            "monthly_actual":   monthly_actual,
            "dias_laborados":   dias_laborados,
            "prod_mensual":     prod_mensual,
            "today_actual":     today_actual,
            "daily_target":     round(daily_from_month, 1),
            "month_days":       month_days,
        })

    return sorted(result, key=lambda x: x["prod_mensual"], reverse=True)


def get_all_entries_for_month(year: int, month: int,
                              tiendas_filter: list | None = None) -> list[dict]:
    yf = _year_filter("se.entry_date")
    mf = _month_filter("se.entry_date")
    with get_conn() as conn:
        base_select = """SELECT se.id, se.entry_date, se.units_sold,
                                se.units_gana_plus, se.units_kiosko,
                                se.order_number, se.notes, se.created_at,
                                u.associate_number, u.name, u.tienda,
                                u.determinante"""
        if tiendas_filter:
            ph = ",".join(["%s" if _USE_PG else "?"] * len(tiendas_filter))
            cur = _exec(conn,
                        f"{base_select}"
                        f" FROM sales_entries se"
                        f" JOIN users u ON u.id = se.user_id"
                        f" WHERE {yf} AND {mf} AND u.tienda IN ({ph}) {_EXCL}"
                        f" ORDER BY u.name, se.entry_date, se.id",
                        (str(year), f"{month:02d}", *tiendas_filter))
        else:
            cur = _exec(conn,
                        f"{base_select}"
                        f" FROM sales_entries se"
                        f" JOIN users u ON u.id = se.user_id"
                        f" WHERE {yf} AND {mf} {_EXCL}"
                        f" ORDER BY u.name, se.entry_date, se.id",
                        (str(year), f"{month:02d}"))
        rows = _fetchall(cur)
    for r in rows:
        r["entry_date"] = str(r["entry_date"])
    return rows


# ────────────────────────────────────────────────────────────────────────────
#  EDICIÓN DE ENTRADAS
# ────────────────────────────────────────────────────────────────────────────

def get_sales_entry(entry_id: int, user_id: int) -> dict | None:
    """Obtiene un registro de venta específico del usuario."""
    with get_conn() as conn:
        cur = _exec(conn,
                    """SELECT id, entry_date, units_sold, units_gana_plus, units_kiosko
                       FROM sales_entries WHERE id=? AND user_id=?""",
                    (entry_id, user_id))
        row = _fetchone(cur)
    if row:
        row["entry_date"] = str(row["entry_date"])
    return row


def update_sales_entry(entry_id: int, user_id: int,
                       gana_plus: float, kiosko: float) -> bool:
    """Actualiza Gana+ y Kiosco de un registro. Solo el dueño puede modificarlo."""
    total = round(gana_plus + kiosko, 2)
    with get_conn() as conn:
        cur = _exec(conn,
                    """UPDATE sales_entries
                       SET units_gana_plus=?, units_kiosko=?, units_sold=?
                       WHERE id=? AND user_id=?""",
                    (gana_plus, kiosko, total, entry_id, user_id))
        return cur.rowcount > 0


def get_all_sales_entries(user_id: int) -> list:
    """Retorna todas las entradas de venta de un usuario (para retro-monedas)."""
    with get_conn() as conn:
        cur = _exec(conn,
                    """SELECT id, units_gana_plus, units_kiosko
                       FROM sales_entries WHERE user_id=?""",
                    (user_id,))
        return _fetchall(cur)


# ────────────────────────────────────────────────────────────────────────────
#  MATRIZ ADMIN (vista tipo Excel)
# ────────────────────────────────────────────────────────────────────────────

def get_team_matrix(year: int, month: int,
                    tiendas_filter: list | None = None) -> dict:
    """Retorna datos en formato de matriz: miembros x dias con Gana+/Kiosco."""
    today         = date.today()
    days_in_month = calendar.monthrange(year, month)[1]
    last_day      = today.day if (year == today.year and month == today.month) \
                    else days_in_month
    day_range     = list(range(1, last_day + 1))

    all_entries = get_all_entries_for_month(year, month,
                                            tiendas_filter=tiendas_filter)

    # Mapa: associate_number -> {day_num: {gana_plus, kiosko}}
    entry_map: dict[str, dict[int, dict]] = {}
    for e in all_entries:
        assoc   = e["associate_number"]
        day_num = int(str(e["entry_date"]).split("-")[2])
        entry_map.setdefault(assoc, {}).setdefault(
            day_num, {"gana_plus": 0.0, "kiosko": 0.0}
        )
        entry_map[assoc][day_num]["gana_plus"] += float(e.get("units_gana_plus") or 0)
        entry_map[assoc][day_num]["kiosko"]    += float(e.get("units_kiosko")    or 0)

    members = []
    for u in get_all_users(tiendas_filter=tiendas_filter):
        assoc        = u["associate_number"]
        days         = entry_map.get(assoc, {})
        total_gana   = sum(d["gana_plus"] for d in days.values())
        total_kiosko = sum(d["kiosko"]    for d in days.values())
        members.append({
            "name":             u["name"],
            "associate_number": assoc,
            "tienda":           u["tienda"],
            "total_gana":       total_gana,
            "total_kiosko":     total_kiosko,
            "days":             days,
        })

    return {
        "members":   sorted(members, key=lambda x: x["name"].casefold()),
        "day_range": day_range,
    }


# ────────────────────────────────────────────────────────────────────────────
#  PEDIDOS OMNICANAL
# ────────────────────────────────────────────────────────────────────────────

ORDER_STATUSES = ["Pendiente", "Embarcado", "Entregado", "Cancelado", "Devolucion", "Pagado"]
ORDER_TYPES    = ["KIOSCO", "GANA+"]
IVA            = 0.16


def _init_orders_table(conn) -> None:
    """Crea la tabla orders si no existe."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            tienda          TEXT    NOT NULL,
            order_number    TEXT    NOT NULL,
            amount_pesos    REAL    NOT NULL,
            amount_sin_iva  REAL    NOT NULL,
            sale_date       TEXT    NOT NULL,
            type            TEXT    NOT NULL,
            status          TEXT    NOT NULL DEFAULT 'Pendiente',
            created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


def _ensure_orders_table() -> None:
    """Garantiza que la tabla orders exista en SQLite."""
    if not _USE_PG:
        with get_conn() as conn:
            _init_orders_table(conn)


_ensure_orders_table()


def order_number_exists(order_number: str) -> bool:
    with get_conn() as conn:
        cur = _exec(conn, "SELECT id FROM orders WHERE order_number=?", (order_number,))
        return _fetchone(cur) is not None


def create_order(user_id: int, tienda: str, order_number: str,
                 amount_pesos: float, sale_date: str, order_type: str) -> int:
    """Inserta un pedido nuevo. Retorna el id."""
    sin_iva = round(amount_pesos / (1 + IVA), 2)
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO orders
               (user_id, tienda, order_number, amount_pesos, amount_sin_iva, sale_date, type)
               VALUES (?,?,?,?,?,?,?)""",
            (user_id, tienda, order_number, amount_pesos, sin_iva, sale_date, order_type),
        )
        return cur.lastrowid


def get_orders_by_user_month(user_id: int, year: int, month: int) -> list:
    """Pedidos de UN asociado en un mes."""
    prefix = f"{year}-{month:02d}"
    with get_conn() as conn:
        cur = _exec(conn,
                    """SELECT o.*, u.name as associate_name, u.associate_number
                       FROM orders o JOIN users u ON o.user_id = u.id
                       WHERE o.user_id=? AND o.sale_date LIKE ?
                       ORDER BY o.sale_date DESC, o.id DESC""",
                    (user_id, f"{prefix}%"))
        return _fetchall(cur)


def get_orders_summary_month(tienda: str, year: int, month: int) -> dict:
    """Resumen de pedidos de UNA tienda en un mes (para review panel)."""
    prefix = f"{year}-{month:02d}"
    with get_conn() as conn:
        # Todos los pedidos de la tienda
        cur = _exec(conn,
                    """SELECT o.*, u.name as associate_name, u.associate_number
                       FROM orders o JOIN users u ON o.user_id = u.id
                       WHERE o.tienda=? AND o.sale_date LIKE ?
                       ORDER BY o.sale_date DESC, o.id DESC""",
                    (tienda, f"{prefix}%"))
        orders = _fetchall(cur)

        # Meta de la tienda
        cur2 = _exec(conn,
                     "SELECT goal FROM store_goals WHERE tienda=? AND year=? AND month=?",
                     (tienda, year, month))
        goal_row = _fetchone(cur2)
        goal = float(goal_row["goal"]) if goal_row else 0.0

    total_pesos   = sum(float(o["amount_pesos"])   for o in orders)
    total_sin_iva = sum(float(o["amount_sin_iva"]) for o in orders)
    kiosco_pesos  = sum(float(o["amount_pesos"]) for o in orders if o["type"] == "KIOSCO")
    gana_pesos    = sum(float(o["amount_pesos"]) for o in orders if o["type"] == "GANA+")
    alcance       = round(total_pesos / goal * 100, 1) if goal > 0 else 0

    # Agrupado por asociado
    assoc_map: dict = {}
    for o in orders:
        k = o["associate_number"]
        assoc_map.setdefault(k, {
            "name": o["associate_name"], "associate_number": k,
            "orders": 0, "pesos": 0.0, "sin_iva": 0.0,
            "kiosco": 0.0, "gana": 0.0,
        })
        assoc_map[k]["orders"] += 1
        assoc_map[k]["pesos"]  += float(o["amount_pesos"])
        assoc_map[k]["sin_iva"] += float(o["amount_sin_iva"])
        if o["type"] == "KIOSCO":
            assoc_map[k]["kiosco"] += float(o["amount_pesos"])
        else:
            assoc_map[k]["gana"]   += float(o["amount_pesos"])

    return {
        "orders":       orders,
        "associates":   sorted(assoc_map.values(), key=lambda x: x["pesos"], reverse=True),
        "total_orders": len(orders),
        "total_pesos":  total_pesos,
        "total_sin_iva": total_sin_iva,
        "kiosco_pesos": kiosco_pesos,
        "gana_pesos":   gana_pesos,
        "goal":         goal,
        "alcance":      alcance,
    }


def update_order_status(order_id: int, user_id: int, new_status: str) -> bool:
    """Cambia el estatus de un pedido. Solo el dueno puede modificarlo."""
    with get_conn() as conn:
        cur = _exec(conn,
                    "UPDATE orders SET status=? WHERE id=? AND user_id=?",
                    (new_status, order_id, user_id))
        return cur.rowcount > 0


# ────────────────────────────────────────────────────────────────────────────
#  CONCENTRADO DE VENTAS POR TIENDA
# ────────────────────────────────────────────────────────────────────────────

def get_concentrado_tienda(tienda: str, year: int, month: int) -> dict:
    """
    Retorna todos los pedidos del mes para una tienda, agrupados por asociado.
    Incluye: lista plana de entradas, resumen por asociado, totales generales.
    Cada asociado incluye montos por canal (Gana+/Kiosko), total monto,
    alcance sobre su meta individual y alcance sobre el total de la tienda.
    """
    prefix = f"{year}-{month:02d}"

    with get_conn() as conn:
        cur = _exec(conn,
                    """SELECT s.id, s.entry_date, s.order_number,
                              s.units_sold, s.units_gana_plus, s.units_kiosko,
                              s.status, s.amount_sin_iva,
                              s.almacen, s.descripcion,
                              u.name AS associate_name,
                              u.associate_number
                       FROM sales_entries s
                       JOIN users u ON s.user_id = u.id
                       WHERE u.tienda = ?
                         AND s.entry_date LIKE ?
                       ORDER BY s.entry_date DESC, u.name, s.id DESC""",
                    (tienda, f"{prefix}%"))
        entries = _fetchall(cur)

        # Metas individuales de todos los asesores de la tienda para este mes
        cur2 = _exec(conn,
                     """SELECT u.associate_number, um.meta_tienda, um.plantilla
                        FROM user_meta um
                        JOIN users u ON um.user_id = u.id
                        WHERE u.tienda = ? AND um.year = ? AND um.month = ?""",
                     (tienda, year, month))
        meta_rows = _fetchall(cur2)

    meta_map = {r["associate_number"]: r for r in meta_rows}

    for e in entries:
        e["entry_date"] = str(e["entry_date"])
        e["amount_sin_iva"] = float(e["amount_sin_iva"] or 0)

    _NO_CUENTA = {"cancelado", "devolucion"}

    # Resumen por asociado — solo pedidos activos (excluye cancelado/devolucion)
    assoc_map: dict = {}
    for e in entries:
        k = e["associate_number"]
        # El asesor aparece en el mapa aunque todos sus pedidos sean cancelados
        assoc_map.setdefault(k, {
            "name":             e["associate_name"],
            "associate_number": k,
            "total":        0,
            "gana":         0,
            "kiosko":       0,
            "monto_gana":   0.0,
            "monto_kiosko": 0.0,
            "monto_total":  0.0,
        })
        # Cancelado / devolucion: no suman en ninguna cifra
        if (e["status"] or "pendiente") in _NO_CUENTA:
            continue

        units_gana   = int(e["units_gana_plus"] or 0)
        units_kiosko = int(e["units_kiosko"]    or 0)
        monto        = float(e["amount_sin_iva"] or 0)

        assoc_map[k]["total"]       += int(e["units_sold"] or 0)
        assoc_map[k]["gana"]        += units_gana
        assoc_map[k]["kiosko"]      += units_kiosko
        assoc_map[k]["monto_total"] += monto
        if units_gana > 0:
            assoc_map[k]["monto_gana"]   += monto
        elif units_kiosko > 0:
            assoc_map[k]["monto_kiosko"] += monto

    associates = sorted(assoc_map.values(), key=lambda x: x["total"], reverse=True)

    total_general = sum(a["total"]       for a in associates)
    total_gana    = sum(a["gana"]        for a in associates)
    total_kiosko  = sum(a["kiosko"]      for a in associates)
    total_monto   = sum(a["monto_total"] for a in associates)

    # Alcances por asesor
    for a in associates:
        meta = meta_map.get(a["associate_number"])
        if meta and meta.get("meta_tienda") and meta.get("plantilla"):
            # objetivo = meta_tienda / plantilla  (en pesos, igual que en Mi Productividad)
            objetivo = meta["meta_tienda"] / max(int(meta["plantilla"]), 1)
            a["meta_objetivo"] = round(objetivo, 2)
            a["meta_pct"] = round(a["monto_total"] / objetivo * 100, 1) if objetivo > 0 else None
        else:
            a["meta_objetivo"] = None
            a["meta_pct"] = None
        # % del monto total de la tienda que aporta este asesor
        a["pct_tienda"] = round(a["monto_total"] / total_monto * 100, 1) if total_monto > 0 else 0.0

    # Presupuesto de tienda: tomamos el primer meta_tienda no nulo del periodo
    presupuesto_tienda = 0.0
    plantilla_tienda   = 0
    for r in meta_rows:
        if r.get("meta_tienda"):
            presupuesto_tienda = float(r["meta_tienda"])
            plantilla_tienda   = int(r.get("plantilla") or 1)
            break

    alcance_tienda_pct = (
        round(total_monto / presupuesto_tienda * 100, 1)
        if presupuesto_tienda > 0 else 0.0
    )

    return {
        "entries":            entries,
        "associates":         associates,
        "total_general":      total_general,
        "total_gana":         total_gana,
        "total_kiosko":       total_kiosko,
        "total_monto":        total_monto,
        "presupuesto_tienda": presupuesto_tienda,
        "plantilla_tienda":   plantilla_tienda,
        "alcance_tienda_pct": alcance_tienda_pct,
    }


def get_entry_by_tienda(entry_id: int, tienda: str) -> dict | None:
    """Retorna una entrada si pertenece a la tienda. Incluye user_id y canal."""
    with get_conn() as conn:
        cur = _exec(conn,
                    """SELECT s.id, s.status, s.units_gana_plus, s.units_kiosko,
                              s.user_id
                       FROM sales_entries s
                       JOIN users u ON s.user_id = u.id
                       WHERE s.id = ? AND u.tienda = ?""",
                    (entry_id, tienda))
        return _fetchone(cur)


def update_entry_status(entry_id: int, tienda: str, new_status: str) -> bool:
    """Cambia el status de un pedido. Solo si pertenece a la tienda."""
    allowed = {"pendiente", "embarcado", "entregado", "cancelado", "devolucion", "pagado"}
    if new_status not in allowed:
        return False
    with get_conn() as conn:
        cur = _exec(conn,
                    """UPDATE sales_entries SET status=?
                       WHERE id=?
                         AND user_id IN (SELECT id FROM users WHERE tienda=?)""",
                    (new_status, entry_id, tienda))
        return cur.rowcount > 0


def get_sales_entry_by_owner(entry_id: int, user_id: int) -> dict | None:
    """Retorna una entrada solo si pertenece al usuario."""
    with get_conn() as conn:
        cur = _exec(conn,
                    "SELECT * FROM sales_entries WHERE id=? AND user_id=?",
                    (entry_id, user_id))
        return _fetchone(cur)


def update_entry_order_and_amount(entry_id: int, user_id: int,
                                   order_number: str, amount_sin_iva: float) -> bool:
    """Corrige numero de pedido y monto de una entrada propia."""
    num = order_number.strip() or None
    with get_conn() as conn:
        cur = _exec(conn,
                    """UPDATE sales_entries
                       SET order_number=?, amount_sin_iva=?
                       WHERE id=? AND user_id=?""",
                    (num, amount_sin_iva, entry_id, user_id))
        return cur.rowcount > 0


# ── MENSAJES MOTIVADORES ───────────────────────────────────────────────────

_MENSAJES = [
    # (min_pct, max_pct, mensaje, color_css)
    (  0,  14, "Cada pedido es un paso adelante. Arranca con todo!",           "blue"   ),
    ( 15,  29, "Buen arranque! Ya llevas el 15%. El ritmo es clave.",           "blue"   ),
    ( 30,  44, "30% completado. Vas bien encaminado, no bajes el ritmo!",      "green"  ),
    ( 45,  59, "Ya estas a mitad del camino. La constancia gana siempre!",     "green"  ),
    ( 60,  74, "60% logrado! La meta ya se ve, sigue empujando!",              "yellow" ),
    ( 75,  89, "75% del objetivo! Ultimo tramo, dale con todo!",               "yellow" ),
    ( 90,  99, "Casi lista! A un empujon de alcanzar tu meta del mes!",        "orange" ),
    (100, 114, "META CUMPLIDA! Excelente trabajo este mes!",                   "walmart" ),
    (115, 129, "115% de la meta! Eres una maquina de ventas!",                "walmart" ),
    (130, 999, "Mas del 130%! Nivel leyenda desbloqueado. Increible!",         "purple" ),
]

_HITOS = [0, 15, 30, 45, 60, 75, 90, 100, 115, 130]


def get_motivational_message(user_id: int, year: int, month: int) -> dict | None:
    """
    Retorna el mensaje motivador correspondiente al % de avance
    a la meta individual. Retorna None si no hay meta configurada.
    """
    meta = get_user_meta(user_id, year, month)
    if not meta or not meta.get("meta_tienda") or not meta.get("plantilla"):
        return None

    objetivo_individual = meta["meta_tienda"] / meta["plantilla"]
    if objetivo_individual <= 0:
        return None

    # Total pedidos del mes
    prefix = f"{year}-{month:02d}"
    with get_conn() as conn:
        cur = _exec(conn,
                    f"SELECT COUNT(*) AS n FROM sales_entries "
                    f"WHERE user_id=? AND entry_date LIKE ? {_EXCL}",
                    (user_id, f"{prefix}%"))
        row   = _fetchone(cur)
        total = int(row["n"] if row else 0)

    pct = (total / objetivo_individual) * 100

    msg_row = _MENSAJES[0]
    for m in _MENSAJES:
        if pct >= m[0]:
            msg_row = m

    # Hito actual (multiplo de 15 alcanzado)
    hito = 0
    for h in _HITOS:
        if pct >= h:
            hito = h

    return {
        "pct":       round(pct, 1),
        "total":     total,
        "objetivo":  round(objetivo_individual, 1),
        "mensaje":   msg_row[2],
        "color":     msg_row[3],
        "hito":      hito,
    }


# ────────────────────────────────────────────────────────────────────────────
#  PRESUPUESTOS POR TIENDA (carga masiva via Excel)
# ────────────────────────────────────────────────────────────────────────────

def get_store_budget(determinante: str, year: int, month: int) -> float:
    """Presupuesto mensual en pesos de la tienda por determinante, 0 si no existe."""
    ph = "%s" if _USE_PG else "?"
    with get_conn() as conn:
        cur = _exec(
            conn,
            f"SELECT presupuesto FROM store_budgets WHERE determinante={ph} AND year={ph} AND month={ph}",
            (determinante, year, month),
        )
        row = _fetchone(cur)
        return float(row["presupuesto"]) if row else 0.0


def get_store_daily_budget(determinante: str, year: int, month: int, day: int) -> float:
    """Presupuesto del dia especifico, 0 si no existe."""
    ph = "%s" if _USE_PG else "?"
    with get_conn() as conn:
        cur = _exec(
            conn,
            f"SELECT presupuesto FROM store_daily_budgets"
            f" WHERE determinante={ph} AND year={ph} AND month={ph} AND day={ph}",
            (determinante, year, month, day),
        )
        row = _fetchone(cur)
        return float(row["presupuesto"]) if row else 0.0


def get_store_daily_budgets_month(determinante: str, year: int, month: int) -> dict[int, float]:
    """Todos los presupuestos diarios del mes. Retorna {dia: presupuesto}."""
    ph = "%s" if _USE_PG else "?"
    with get_conn() as conn:
        cur = _exec(
            conn,
            f"SELECT day, presupuesto FROM store_daily_budgets"
            f" WHERE determinante={ph} AND year={ph} AND month={ph} ORDER BY day",
            (determinante, year, month),
        )
        return {r["day"]: float(r["presupuesto"]) for r in _fetchall(cur)}


def upsert_store_budgets(rows: list[dict]) -> int:
    """
    Inserta/actualiza presupuestos mensuales y diarios de tiendas.
    rows = [{determinante, tienda, year, month, presupuesto_mensual,
             dias: {1: X, 2: Y, ...}}]
    Retorna cantidad de filas mensuales procesadas.
    """
    ph = "%s" if _USE_PG else "?"
    count = 0
    with get_conn() as conn:
        for b in rows:
            det   = b["determinante"]
            tiend = b.get("tienda", "")
            yr    = b["year"]
            mo    = b["month"]
            pres  = b["presupuesto"]
            dias  = b.get("dias", {})

            # Mensual
            if _USE_PG:
                _exec(conn,
                      "INSERT INTO store_budgets (determinante, tienda, year, month, presupuesto)"
                      " VALUES (%s,%s,%s,%s,%s)"
                      " ON CONFLICT (determinante, year, month)"
                      " DO UPDATE SET presupuesto=EXCLUDED.presupuesto, tienda=EXCLUDED.tienda",
                      (det, tiend, yr, mo, pres))
            else:
                _exec(conn,
                      "INSERT INTO store_budgets (determinante, tienda, year, month, presupuesto)"
                      " VALUES (?,?,?,?,?)"
                      " ON CONFLICT (determinante, year, month)"
                      " DO UPDATE SET presupuesto=excluded.presupuesto, tienda=excluded.tienda",
                      (det, tiend, yr, mo, pres))
            count += 1

            # Diarios
            for day, pres_dia in dias.items():
                if _USE_PG:
                    _exec(conn,
                          "INSERT INTO store_daily_budgets (determinante, year, month, day, presupuesto)"
                          " VALUES (%s,%s,%s,%s,%s)"
                          " ON CONFLICT (determinante, year, month, day)"
                          " DO UPDATE SET presupuesto=EXCLUDED.presupuesto",
                          (det, yr, mo, int(day), float(pres_dia)))
                else:
                    _exec(conn,
                          "INSERT INTO store_daily_budgets (determinante, year, month, day, presupuesto)"
                          " VALUES (?,?,?,?,?)"
                          " ON CONFLICT (determinante, year, month, day)"
                          " DO UPDATE SET presupuesto=excluded.presupuesto",
                          (det, yr, mo, int(day), float(pres_dia)))
    return count


def get_all_tiendas() -> list[str]:
    """Todas las tiendas distintas registradas en users (sin blancos)."""
    with get_conn() as conn:
        cur = _exec(
            conn,
            "SELECT DISTINCT tienda FROM users WHERE tienda != '' ORDER BY tienda",
            (),
        )
        return [r["tienda"] for r in _fetchall(cur)]


def get_all_store_budgets(year: int, month: int) -> list[dict]:
    """Todos los presupuestos mensuales guardados para un periodo."""
    ph = "%s" if _USE_PG else "?"
    with get_conn() as conn:
        cur = _exec(
            conn,
            f"SELECT determinante, tienda, presupuesto FROM store_budgets"
            f" WHERE year={ph} AND month={ph} ORDER BY tienda",
            (year, month),
        )
        return _fetchall(cur)


def get_stats_by_group(year: int, month: int, group_col: str) -> list[dict]:
    """
    Estadisticas agrupadas por 'squad' o 'distrito'.
    Retorna lista ordenada por pedidos desc con:
      grupo, num_asesores, total_pedidos, total_unidades,
      presupuesto_total, alcance_pct
    """
    assert group_col in ("squad", "distrito"), "grupo invalido"
    yf = _year_filter("se.entry_date")
    mf = _month_filter("se.entry_date")
    ph = "%s" if _USE_PG else "?"
    with get_conn() as conn:
        # Ventas del mes agrupadas por el campo del usuario
        cur = _exec(conn, f"""
            SELECT u.{group_col}          AS grupo,
                   COUNT(DISTINCT u.id)   AS num_asesores,
                   COUNT(se.id)           AS total_pedidos,
                   COALESCE(SUM(se.units_sold), 0) AS total_unidades
            FROM users u
            LEFT JOIN sales_entries se
                   ON se.user_id = u.id
                  AND {yf} AND {mf}
            WHERE u.role = 'user'
              AND u.{group_col} != ''
            GROUP BY u.{group_col}
            ORDER BY total_pedidos DESC
        """, (str(year), f"{month:02d}"))
        rows = _fetchall(cur)

    # Para cada grupo sumar los presupuestos de sus determinantes
    for r in rows:
        grp = r["grupo"]
        with get_conn() as conn:
            cur2 = _exec(conn, f"""
                SELECT COALESCE(SUM(sb.presupuesto), 0) AS total_pres
                FROM store_budgets sb
                WHERE sb.year  = {ph}
                  AND sb.month = {ph}
                  AND sb.determinante IN (
                      SELECT DISTINCT determinante FROM users
                      WHERE {group_col} = {ph} AND role = 'user'
                  )
            """, (year, month, grp))
            pres = (_fetchone(cur2) or {}).get("total_pres", 0) or 0
        r["presupuesto_total"] = round(float(pres), 0)
        r["alcance_pct"] = (
            round(r["total_unidades"] / pres * 100, 1) if pres > 0 else None
        )
    return rows
