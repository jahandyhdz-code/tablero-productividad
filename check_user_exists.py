import sqlite3
conn = sqlite3.connect('ventas.db')
# Buscar ese numero especifico
rows = conn.execute(
    "SELECT id, associate_number, name, role FROM users WHERE associate_number = '7095302'"
).fetchall()
print("Resultado busqueda 7095302:", rows)

# Ver todos los usuarios
all_u = conn.execute(
    "SELECT id, associate_number, name, role FROM users ORDER BY id"
).fetchall()
print("\nTodos los usuarios:")
for r in all_u:
    print(r)
conn.close()
