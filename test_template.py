"""Test rapido del template de concentrado."""
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError, UndefinedError
import database as db
import sys

MONTHS_ES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

try:
    env = Environment(loader=FileSystemLoader("templates"))
    t   = env.get_template("partials/concentrado.html")
    data = db.get_concentrado_tienda("1a de Mayo", 2026, 7)
    print("Keys DB:", list(data.keys()))
    print("presupuesto_tienda:", data["presupuesto_tienda"])
    print("alcance_tienda_pct:", data["alcance_tienda_pct"])
    html = t.render(
        data=data, tienda="1a de Mayo", year=2026, month=7,
        months_es=MONTHS_ES, me="7095302"
    )
    print(f"OK — template renderizo, {len(html)} chars")
except (TemplateSyntaxError, UndefinedError) as e:
    print(f"ERROR TEMPLATE: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    sys.exit(1)
