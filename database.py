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
        created_at           TEXT    NOT NULL DEFAULT (datetime('now'))
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
        admin_tiendas        TEXT   DEFAULT NULL,
        created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
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
    _add_col_if_missing("sales_entries", "units_gana_plus", "REAL NOT NULL DEFAULT 0")
    _add_col_if_missing("sales_entries", "units_kiosko",    "REAL NOT NULL DEFAULT 0")


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
                f"SELECT id,associate_number,name,role,tienda,admin_tiendas,created_at"
                f" FROM users WHERE tienda IN ({ph}) ORDER BY name",
                tiendas_filter,
            )
        else:
            cur = _exec(
                conn,
                "SELECT id,associate_number,name,role,tienda,admin_tiendas,created_at"
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


def associate_number_exists(associate_number: str) -> bool:
    with get_conn() as conn:
        cur = _exec(conn,
                    "SELECT 1 FROM users WHERE associate_number = ?",
                    (associate_number.strip(),))
        return _fetchone(cur) is not None


def delete_user(user_id: int) -> None:
    with get_conn() as conn:
        _exec(conn, "DELETE FROM sessions      WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM rest_days     WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM sales_entries WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM sales_targets WHERE user_id = ?", (user_id,))
        _exec(conn, "DELETE FROM users          WHERE id      = ?", (user_id,))


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
#  REST DAYS
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

def add_sales_entry(user_id: int, entry_date: str, units_sold: float,
                    gana_plus: float = 0.0, kiosko: float = 0.0) -> int:
    with get_conn() as conn:
        if _USE_PG:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO sales_entries
                (user_id, entry_date, units_sold, units_gana_plus, units_kiosko)
                VALUES (%s,%s,%s,%s,%s) RETURNING id
            """, (user_id, entry_date, units_sold, gana_plus, kiosko))
            return cur.fetchone()[0]
        else:
            cur = conn.execute("""
                INSERT INTO sales_entries
                (user_id, entry_date, units_sold, units_gana_plus, units_kiosko)
                VALUES (?,?,?,?,?)
            """, (user_id, entry_date, units_sold, gana_plus, kiosko))
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
                               units_gana_plus, units_kiosko, created_at
                        FROM sales_entries
                        WHERE user_id=? AND {yf} AND {mf}
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
                    """SELECT COALESCE(SUM(units_sold),0) as total FROM sales_entries
                       WHERE user_id=? AND entry_date>=? AND entry_date<=?""",
                    (user_id, week_start.isoformat(), week_end.isoformat()))
        row = _fetchone(cur)
    return float(row["total"]) if row else 0.0


def get_sales_for_day(user_id: int, day: date) -> float:
    with get_conn() as conn:
        cur = _exec(conn,
                    """SELECT COALESCE(SUM(units_sold),0) as total FROM sales_entries
                       WHERE user_id=? AND entry_date=?""",
                    (user_id, day.isoformat()))
        row = _fetchone(cur)
    return float(row["total"]) if row else 0.0


# ────────────────────────────────────────────────────────────────────────────
#  PRODUCTIVITY CALCULATIONS
# ────────────────────────────────────────────────────────────────────────────

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


def get_productivity_metrics(user_id: int, year: int, month: int) -> dict:
    today = date.today()
    days_in_month  = calendar.monthrange(year, month)[1]
    monthly_target = get_sales_target(user_id, year, month) or 0.0

    rest_days = get_rest_days_for_month(user_id, year, month)
    working_days_month = max(days_in_month - len(rest_days), 1)
    daily_target = monthly_target / working_days_month if monthly_target else 0.0

    today_is_rest = today.isoformat() in rest_days
    today_target  = 0.0 if today_is_rest else daily_target

    week_start, week_end = commercial_week(today)
    working_days_week = sum(
        1 for i in range(7)
        if (week_start + timedelta(days=i)).month == month
        and (week_start + timedelta(days=i)).isoformat() not in rest_days
    )
    weekly_target = daily_target * working_days_week

    monthly_entries = get_sales_for_month(user_id, year, month)
    monthly_actual  = sum(e["units_sold"] for e in monthly_entries)
    weekly_actual   = get_sales_for_week(user_id, week_start, week_end)
    daily_actual    = get_sales_for_day(user_id, today)
    daily_diff      = round(daily_actual - today_target, 1)

    daily_map: dict[str, float] = {}
    for e in monthly_entries:
        d = str(e["entry_date"])
        daily_map[d] = daily_map.get(d, 0.0) + e["units_sold"]

    chart_labels = list(range(1, days_in_month + 1))
    chart_data   = [daily_map.get(date(year, month, d).isoformat(), 0.0) for d in chart_labels]
    chart_rest   = [date(year, month, d).isoformat() in rest_days for d in chart_labels]

    return {
        "daily":   {"actual": daily_actual,   "target": round(today_target, 1),
                    "pct": _pct(daily_actual, today_target), "diff": daily_diff},
        "weekly":  {"actual": weekly_actual,  "target": round(weekly_target, 1),
                    "pct": _pct(weekly_actual, weekly_target)},
        "monthly": {"actual": monthly_actual, "target": monthly_target,
                    "pct": _pct(monthly_actual, monthly_target)},
        "chart_labels":  chart_labels,
        "chart_data":    chart_data,
        "chart_rest":    chart_rest,
        "rest_days":     rest_days,
        "first_weekday": date(year, month, 1).weekday(),
        "entries":       monthly_entries,
        "today":         today.isoformat(),
        "has_target":    monthly_target > 0,
        "daily_target":  round(daily_target, 1),
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
        if tiendas_filter:
            ph = ",".join(["%s" if _USE_PG else "?"] * len(tiendas_filter))
            cur = _exec(conn,
                        f"""SELECT se.id, se.entry_date, se.units_sold,
                                   se.units_gana_plus, se.units_kiosko,
                                   se.notes, se.created_at,
                                   u.associate_number, u.name, u.tienda
                            FROM sales_entries se
                            JOIN users u ON u.id = se.user_id
                            WHERE {yf} AND {mf} AND u.tienda IN ({ph})
                            ORDER BY u.name, se.entry_date, se.id""",
                        (str(year), f"{month:02d}", *tiendas_filter))
        else:
            cur = _exec(conn,
                        f"""SELECT se.id, se.entry_date, se.units_sold,
                                   se.units_gana_plus, se.units_kiosko,
                                   se.notes, se.created_at,
                                   u.associate_number, u.name, u.tienda
                            FROM sales_entries se
                            JOIN users u ON u.id = se.user_id
                            WHERE {yf} AND {mf}
                            ORDER BY u.name, se.entry_date, se.id""",
                        (str(year), f"{month:02d}"))
        rows = _fetchall(cur)
    for r in rows:
        r["entry_date"] = str(r["entry_date"])
    return rows
