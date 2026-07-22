import sqlite3

conn = sqlite3.connect('ventas.db')

user_id = 12  # 7095302 JAHANDY admin

# Borrar en cascada (mismo orden que delete_user)
conn.execute("DELETE FROM pet_items WHERE pet_id IN (SELECT id FROM pets WHERE user_id=?)", (user_id,))
conn.execute("DELETE FROM pet_actions_log WHERE pet_id IN (SELECT id FROM pets WHERE user_id=?)", (user_id,))
conn.execute("DELETE FROM pets          WHERE user_id=?", (user_id,))
conn.execute("DELETE FROM user_meta     WHERE user_id=?", (user_id,))
conn.execute("DELETE FROM game_plays    WHERE user_id=?", (user_id,))
conn.execute("DELETE FROM orders        WHERE user_id=?", (user_id,))
conn.execute("DELETE FROM sessions      WHERE user_id=?", (user_id,))
conn.execute("DELETE FROM rest_days     WHERE user_id=?", (user_id,))
conn.execute("DELETE FROM sales_entries WHERE user_id=?", (user_id,))
conn.execute("DELETE FROM sales_targets WHERE user_id=?", (user_id,))
conn.execute("DELETE FROM users         WHERE id=?",      (user_id,))
conn.commit()

remaining = conn.execute("SELECT id, associate_number, name, role FROM users ORDER BY id").fetchall()
print("Usuarios restantes:")
for r in remaining:
    print(r)
print("\nListo! 7095302 eliminado, ya puedes volver a crearlo.")
conn.close()
