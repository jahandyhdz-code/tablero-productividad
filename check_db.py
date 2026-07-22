import sqlite3
conn = sqlite3.connect('ventas.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print('TABLAS EN EL DB CORRECTO:')
for t in tables:
    c.execute(f"SELECT COUNT(*) FROM [{t[0]}]")
    print(f"  {t[0]}: {c.fetchone()[0]} filas")
conn.close()
