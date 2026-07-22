import sqlite3, json

conn = sqlite3.connect('ventas.db')

# Tiendas de JAHANDY
at_raw = conn.execute(
    "SELECT admin_tiendas FROM users WHERE id=13"
).fetchone()[0]
tiendas_admin = json.loads(at_raw) if at_raw.startswith('[') else at_raw.split(',')

# Todas las tiendas en store_budgets julio 2026
sb_tiendas = {
    r[0]: r[1]  # tienda_nombre: determinante
    for r in conn.execute(
        "SELECT tienda, determinante FROM store_budgets WHERE year=2026 AND month=7"
    ).fetchall()
}

print("=== ADMIN TIENE 10 TIENDAS ===")
for t in tiendas_admin:
    match = t in sb_tiendas
    print(f"  {'OK' if match else 'FALTA'} | '{t}'")
    if not match:
        # Buscar similar
        similares = [s for s in sb_tiendas if t.lower()[:6] in s.lower()]
        if similares:
            print(f"         Posible en budget: {similares[:3]}")

conn.close()
