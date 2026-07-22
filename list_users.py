import sqlite3
conn = sqlite3.connect('ventas.db')
c = conn.cursor()
c.execute('SELECT associate_number, name, role, tienda, must_change_password FROM users ORDER BY id')
rows = c.fetchall()
print(f"{'#EMPLEADO':<12} {'NOMBRE':<25} {'ROL':<8} {'TIENDA':<20} {'CAMBIA_PASS'}")
print("-" * 80)
for r in rows:
    print(f"{r[0]:<12} {r[1]:<25} {r[2]:<8} {str(r[3]):<20} {r[4]}")
conn.close()
