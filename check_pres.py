import sqlite3, sys
conn = sqlite3.connect('ventas.db')
cnt_m = conn.execute('SELECT COUNT(*) FROM store_budgets').fetchone()[0]
cnt_d = conn.execute('SELECT COUNT(*) FROM store_daily_budgets').fetchone()[0]
print('store_budgets:', cnt_m)
print('store_daily_budgets:', cnt_d)
conn.close()
