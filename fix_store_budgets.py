import sqlite3

conn = sqlite3.connect('ventas.db')
conn.execute('DROP TABLE IF EXISTS store_budgets')
conn.execute('''
CREATE TABLE store_budgets (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    determinante TEXT    NOT NULL DEFAULT '',
    tienda       TEXT    NOT NULL DEFAULT '',
    year         INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    presupuesto  REAL    NOT NULL,
    UNIQUE (determinante, year, month)
)''')
conn.commit()

# Verificar
for row in conn.execute("SELECT sql FROM sqlite_master WHERE name='store_budgets'"):
    print('Schema OK:', row[0][:80])

conn.close()
print('Listo!')
