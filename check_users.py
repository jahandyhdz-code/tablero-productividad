import sqlite3
conn = sqlite3.connect('ventas.db')
cols = [r[1] for r in conn.execute('PRAGMA table_info(users)').fetchall()]
print('Columnas users:', cols)
conn.close()
