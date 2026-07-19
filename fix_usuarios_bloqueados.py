"""
fix_usuarios_bloqueados.py
Pone must_change_password=0 a TODOS los usuarios normales que quedaron atascados.
Solo los admin-creados por el panel quedan con must_change_password=1.
"""
import sys
try:
    import psycopg2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
    import psycopg2

print("=" * 60)
print("  FIX USUARIOS BLOQUEADOS — Render PostgreSQL")
print("=" * 60)
print()
print("  Pega la External Database URL de Render (ventas-db)")
print("  -> Render dashboard -> ventas-db -> Connections")
print()
pg_url = input("  URL de PostgreSQL: ").strip()

conn = psycopg2.connect(pg_url)
cur  = conn.cursor()

# Cuantos estan bloqueados?
cur.execute("SELECT COUNT(*) FROM users WHERE must_change_password = 1 AND role = 'user'")
total = cur.fetchone()[0]
print(f"\n  Usuarios bloqueados encontrados: {total}")

if total == 0:
    print("  No hay usuarios bloqueados. Todo OK!")
else:
    # Desbloquear a todos los usuarios normales
    cur.execute("UPDATE users SET must_change_password = 0 WHERE role = 'user'")
    conn.commit()
    print(f"  {cur.rowcount} usuarios desbloqueados correctamente.")
    print("  Ya pueden entrar con su numero de asociado y contrasena.")

conn.close()
print()
input("  Presiona Enter para cerrar...")
