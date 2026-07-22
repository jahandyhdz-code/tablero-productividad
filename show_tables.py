import sqlite3
conn = sqlite3.connect('ventas.db')
tablas = [r[0] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()]
print(tablas)
conn.close()
