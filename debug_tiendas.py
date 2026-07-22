import sqlite3, json

conn = sqlite3.connect('ventas.db')

# Ver admin_tiendas de JAHANDY (busca cualquier admin que no sea 000000)
admins = conn.execute(
    "SELECT id, name, admin_tiendas FROM users WHERE role='admin' AND associate_number != '000000'"
).fetchall()

for uid, name, at in admins:
    print(f"\n=== {name} (id={uid}) ===")
    if at:
        tiendas = json.loads(at) if at.startswith('[') else at.split(',')
        print(f"admin_tiendas ({len(tiendas)}):", tiendas)

# Ver muestra de tiendas en store_budgets
print("\n--- Muestra store_budgets.tienda ---")
rows = conn.execute(
    "SELECT determinante, tienda FROM store_budgets WHERE year=2026 AND month=7 LIMIT 20"
).fetchall()
for r in rows:
    print(r)

conn.close()
