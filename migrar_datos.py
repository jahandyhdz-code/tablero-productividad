"""
migrar_datos.py — Copia todos los datos del SQLite local al PostgreSQL de Render.
"""
import sqlite3, sys, json
from pathlib import Path

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("Instalando psycopg2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
    import psycopg2
    import psycopg2.extras

DB_LOCAL = Path(__file__).parent / "ventas.db"

def migrar(pg_url: str):
    print("\n  Conectando a base de datos local...")
    sqlite = sqlite3.connect(DB_LOCAL)
    sqlite.row_factory = sqlite3.Row

    print("  Conectando a PostgreSQL en Render...")
    pg = psycopg2.connect(pg_url)
    pg.autocommit = False
    cur = pg.cursor()

    # ── USUARIOS ──────────────────────────────────────────────────────────────
    print("\n  Migrando usuarios...")
    usuarios = sqlite.execute("SELECT * FROM users ORDER BY id").fetchall()
    migrados = 0
    for u in usuarios:
        cur.execute("""
            INSERT INTO users
              (id, associate_number, name, password_hash, role, tienda,
               must_change_password, admin_tiendas, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (associate_number) DO UPDATE SET
              name=EXCLUDED.name,
              password_hash=EXCLUDED.password_hash,
              role=EXCLUDED.role,
              tienda=EXCLUDED.tienda,
              must_change_password=EXCLUDED.must_change_password,
              admin_tiendas=EXCLUDED.admin_tiendas
        """, (
            u["id"], u["associate_number"], u["name"], u["password_hash"],
            u["role"], u["tienda"], u["must_change_password"],
            u["admin_tiendas"], u["created_at"]
        ))
        migrados += 1
    # Sincronizar el sequence de PostgreSQL para que los nuevos IDs no colisionen
    cur.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))")
    print(f"    {migrados} usuarios migrados")

    # ── METAS ──────────────────────────────────────────────────────────────
    print("  Migrando metas de ventas...")
    targets = sqlite.execute("SELECT * FROM sales_targets").fetchall()
    for t in targets:
        cur.execute("""
            INSERT INTO sales_targets (id, user_id, year, month, target_units)
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT (user_id, year, month) DO UPDATE SET target_units=EXCLUDED.target_units
        """, (t["id"], t["user_id"], t["year"], t["month"], t["target_units"]))
    if targets:
        cur.execute("SELECT setval('sales_targets_id_seq', (SELECT MAX(id) FROM sales_targets))")
    print(f"    {len(targets)} metas migradas")

    # ── VENTAS ────────────────────────────────────────────────────────────────
    print("  Migrando registros de ventas...")
    entries = sqlite.execute("SELECT * FROM sales_entries ORDER BY id").fetchall()
    for e in entries:
        cur.execute("""
            INSERT INTO sales_entries
              (id, user_id, entry_date, units_sold, units_gana_plus, units_kiosko, notes, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING
        """, (
            e["id"], e["user_id"], e["entry_date"], e["units_sold"],
            e["units_gana_plus"] if "units_gana_plus" in e.keys() else 0,
            e["units_kiosko"] if "units_kiosko" in e.keys() else 0,
            e["notes"], e["created_at"]
        ))
    if entries:
        cur.execute("SELECT setval('sales_entries_id_seq', (SELECT MAX(id) FROM sales_entries))")
    print(f"    {len(entries)} registros de ventas migrados")

    # ── DIAS DE DESCANSO ──────────────────────────────────────────────────────
    print("  Migrando dias de descanso...")
    rest = sqlite.execute("SELECT * FROM rest_days").fetchall()
    for r in rest:
        cur.execute("""
            INSERT INTO rest_days (id, user_id, rest_date)
            VALUES (%s,%s,%s)
            ON CONFLICT DO NOTHING
        """, (r["id"], r["user_id"], r["rest_date"]))
    if rest:
        cur.execute("SELECT setval('rest_days_id_seq', (SELECT MAX(id) FROM rest_days))")
    print(f"    {len(rest)} dias de descanso migrados")

    pg.commit()
    sqlite.close()
    pg.close()
    print("\n  Migracion completada sin errores!")


if __name__ == "__main__":
    print("=" * 60)
    print("  MIGRACION DE DATOS — Local a Render")
    print("=" * 60)
    print()
    print("  Necesitas la URL externa de la base de datos de Render.")
    print("  En Render: clic en 'ventas-db' -> 'Connections' -> 'External Database URL'")
    print("  Empieza con: postgresql://...")
    print()
    pg_url = input("  Pega la URL de PostgreSQL aqui: ").strip()
    if not pg_url.startswith("postgresql"):
        print("  ERROR: La URL debe empezar con postgresql://")
        sys.exit(1)
    migrar(pg_url)
    print()
    input("  Presiona Enter para cerrar...")
