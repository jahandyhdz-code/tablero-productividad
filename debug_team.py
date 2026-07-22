import sqlite3, json, unicodedata

conn = sqlite3.connect('ventas.db')

def norm(s):
    return unicodedata.normalize('NFD', s or '').encode('ascii', 'ignore').decode().lower().strip()

# admin_tiendas de JAHANDY
at_raw = conn.execute("SELECT admin_tiendas FROM users WHERE id=13").fetchone()[0]
tf = json.loads(at_raw)
tf_norm = {norm(t): t for t in tf}
print("admin_tiendas:", tf)

# Usuarios con capturas este mes
rows = conn.execute("""
    SELECT u.id, u.name, u.tienda, u.determinante, COUNT(se.id) as pedidos
    FROM users u
    JOIN sales_entries se ON se.user_id = u.id
    WHERE strftime('%Y', se.entry_date) = '2026'
      AND strftime('%m', se.entry_date) = '07'
      AND u.role = 'user'
    GROUP BY u.id
""").fetchall()

print("\n=== Usuarios con capturas julio 2026 ===")
for uid, name, tienda, det, ped in rows:
    match = norm(tienda) in tf_norm
    print(f"  {'OK' if match else 'FALTA'} | {name} | tienda='{tienda}' | det='{det}' | {ped} pedidos")
    if not match:
        print(f"         norm tienda: '{norm(tienda)}'")
        print(f"         norm tf keys: {list(tf_norm.keys())}")

conn.close()
