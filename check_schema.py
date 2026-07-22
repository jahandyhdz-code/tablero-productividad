import sqlite3

conn = sqlite3.connect('ventas.db')
rows = conn.execute(
    "SELECT name, sql FROM sqlite_master WHERE type='table' AND name LIKE 'store%'"
).fetchall()
for name, sql in rows:
    print(f'=== {name} ===')
    print(sql)
    print()

cnt = conn.execute('SELECT COUNT(*) FROM store_budgets').fetchone()[0]
print('FILAS store_budgets:', cnt)
conn.close()
