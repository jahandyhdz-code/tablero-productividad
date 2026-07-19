"""pet_functions.py — Logica de mascotas Tamagotchi."""
from datetime import datetime, timezone
from database import get_conn, _exec, _fetchone, _fetchall, _USE_PG


def _ensure_hunger_column() -> None:
    """Migra la columna hunger_updated_at si no existe."""
    try:
        with get_conn() as conn:
            conn.execute("ALTER TABLE pets ADD COLUMN hunger_updated_at TEXT")
    except Exception:
        pass  # Ya existe, todo bien


_ensure_hunger_column()

# ────────────────────────────────────────────────────────────────────────────
#  MASCOTAS (TAMAGOTCHI)
# ────────────────────────────────────────────────────────────────────────────
#
#  Monedas: KIOSCO = +2 | GANA+ = +3
#  Etapas: huevo -> bebe -> joven -> adulto
#  XP para subir: 0->bebe=1, bebe->joven=80, joven->adulto=250
#  Regresion: >3 dias sin actividad baja etapa o pierde accesorio
#
# Catalogo de items
PET_ITEMS_CATALOG = {
    "comida_basica": {"nombre": "Comida Basica",  "costo": 2,  "xp": 10, "hunger": 30, "emoji": ""},
    "golosina":      {"nombre": "Golosina",        "costo": 5,  "xp": 8,  "hunger": 50, "emoji": ""},
    "medicina":      {"nombre": "Medicina",        "costo": 8,  "xp": 5,  "hunger": 20, "emoji": "", "happiness_bonus": 25},
    "juguete":       {"nombre": "Juguete",         "costo": 10, "xp": 15, "hunger": 0,  "emoji": "", "reusable": True, "happiness_bonus": 15},
    "pelota":        {"nombre": "Pelota",          "costo": 15, "xp": 20, "hunger": 0,  "emoji": "", "reusable": True, "happiness_bonus": 25},
    "sombrero":      {"nombre": "Sombrero",        "costo": 20, "xp": 5,  "hunger": 0,  "emoji": "", "cosmetic": True},
    "collar":        {"nombre": "Collar",          "costo": 20, "xp": 5,  "hunger": 0,  "emoji": "", "cosmetic": True},
    "cama":          {"nombre": "Cama",            "costo": 30, "xp": 10, "hunger": 0,  "emoji": "", "cosmetic": True},
    "casita":        {"nombre": "Casita",          "costo": 40, "xp": 5,  "hunger": 0,  "emoji": "", "cosmetic": True},
}

# XP total necesario por etapa
PET_STAGE_XP = {"huevo": 1, "bebe": 80, "joven": 250, "adulto": 999999}
PET_STAGES   = ["huevo", "bebe", "joven", "adulto"]

COINS_KIOSCO  = 2
COINS_GANA    = 3


def get_pet_by_user(user_id: int) -> dict | None:
    with get_conn() as conn:
        cur = _exec(conn, "SELECT * FROM pets WHERE user_id = ?", (user_id,))
        return _fetchone(cur)


def create_pet(user_id: int, animal_type: str, pet_name: str) -> int:
    with get_conn() as conn:
        if _USE_PG:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO pets (user_id, animal_type, pet_name)
                   VALUES (%s, %s, %s) RETURNING id""",
                (user_id, animal_type, pet_name),
            )
            return cur.fetchone()[0]
        else:
            cur = conn.execute(
                "INSERT INTO pets (user_id, animal_type, pet_name) VALUES (?,?,?)",
                (user_id, animal_type, pet_name),
            )
            return cur.lastrowid


def award_coins(user_id: int, coins: int, reason: str = "") -> dict | None:
    """Otorga monedas a la mascota del usuario. Retorna el pet actualizado."""
    with get_conn() as conn:
        ph = "%s" if _USE_PG else "?"
        cur = _exec(conn, f"SELECT id, coins FROM pets WHERE user_id = {ph}", (user_id,))
        pet = _fetchone(cur)
        if not pet:
            return None
        new_coins = pet["coins"] + coins
        _exec(conn,
              f"UPDATE pets SET coins = {ph}, last_activity = datetime('now') WHERE id = {ph}",
              (new_coins, pet["id"]))
        _exec(conn,
              f"""INSERT INTO pet_actions_log (pet_id, action, detail, coins_delta)
                  VALUES ({ph},{ph},{ph},{ph})""",
              (pet["id"], "earn_coins", reason, coins))
    return get_pet_by_user(user_id)


def feed_pet(user_id: int, item_type: str) -> tuple[bool, str, dict | None]:
    """
    Alimenta/usa un item en la mascota.
    Retorna (ok, mensaje, pet_actualizado).
    """
    item = PET_ITEMS_CATALOG.get(item_type)
    if not item:
        return False, "Item no existe.", None

    with get_conn() as conn:
        ph = "%s" if _USE_PG else "?"
        cur = _exec(conn, f"SELECT * FROM pets WHERE user_id = {ph}", (user_id,))
        pet = _fetchone(cur)
        if not pet:
            return False, "No tienes mascota aun.", None

        costo = item["costo"]
        if pet["coins"] < costo:
            return False, f"No tienes suficientes monedas. Necesitas {costo}.", pet

        # Si es cosmético, guardar en inventario y equipar
        if item.get("cosmetic"):
            # Solo puede tener 1 de cada tipo equipado
            _exec(conn,
                  f"UPDATE pet_items SET equipped = 0 WHERE pet_id = {ph} AND item_type = {ph}",
                  (pet["id"], item_type))
            _exec(conn,
                  f"INSERT INTO pet_items (pet_id, item_type, equipped) VALUES ({ph},{ph},1)",
                  (pet["id"], item_type))
        elif not item.get("reusable"):
            # Item de un solo uso: solo registrar en log
            pass

        new_coins    = pet["coins"] - costo
        new_xp       = pet["xp"] + item["xp"]
        new_hunger   = min(100, pet["hunger"] + item.get("hunger", 0))
        new_happiness = min(100, pet["happiness"] + item.get("happiness_bonus", 0))

        # Verificar evolucion
        new_stage  = pet["stage"]
        stage_idx  = PET_STAGES.index(pet["stage"])
        xp_needed  = PET_STAGE_XP[pet["stage"]]
        evolved    = False
        if new_xp >= xp_needed and stage_idx < len(PET_STAGES) - 1:
            new_stage = PET_STAGES[stage_idx + 1]
            evolved   = True

        _exec(conn,
              f"""UPDATE pets SET coins={ph}, xp={ph}, hunger={ph}, happiness={ph},
                  stage={ph}, last_activity=datetime('now') WHERE id={ph}""",
              (new_coins, new_xp, new_hunger, new_happiness, new_stage, pet["id"]))
        _exec(conn,
              f"""INSERT INTO pet_actions_log (pet_id, action, detail, coins_delta, xp_delta)
                  VALUES ({ph},{ph},{ph},{ph},{ph})""",
              (pet["id"], "feed" if not item.get("cosmetic") else "cosmetic",
               item_type, -costo, item["xp"]))

    updated = get_pet_by_user(user_id)
    if evolved:
        msg = f"Tu mascota evoluciono a {new_stage.upper()}!"
    else:
        msg = f"Usaste {item['nombre']}. +{item['xp']} XP"
    return True, msg, updated


def check_pet_regression(user_id: int) -> tuple[bool, str]:
    """
    Revisa si la mascota debe retroceder de etapa o perder accesorios
    por inactividad (>3 dias). Retorna (hubo_regresion, mensaje).
    """
    pet = get_pet_by_user(user_id)
    if not pet or pet["stage"] in ("huevo", "adulto"):
        # adulto pierde accesorios, no baja de etapa
        if pet and pet["stage"] == "adulto":
            last = datetime.fromisoformat(str(pet["last_activity"]).split(".")[0])
            days_idle = (datetime.utcnow() - last).days
            if days_idle >= 5:
                return _remove_random_accessory(pet), "Tu mascota perdio un accesorio por inactividad."
        return False, ""

    last = datetime.fromisoformat(str(pet["last_activity"]).split(".")[0])
    days_idle = (datetime.utcnow() - last).days
    if days_idle < 3:
        return False, ""

    stage_idx = PET_STAGES.index(pet["stage"])
    new_stage = PET_STAGES[max(0, stage_idx - 1)]
    # Quitar XP para que quede por debajo del umbral anterior
    new_xp = max(0, PET_STAGE_XP.get(new_stage, 0) - 10)
    with get_conn() as conn:
        ph = "%s" if _USE_PG else "?"
        _exec(conn,
              f"UPDATE pets SET stage={ph}, xp={ph}, last_activity=datetime('now') WHERE id={ph}",
              (new_stage, new_xp, pet["id"]))
        _exec(conn,
              f"""INSERT INTO pet_actions_log (pet_id, action, detail)
                  VALUES ({ph},'regression',{ph})""",
              (pet["id"], f"Retrocedio de {pet['stage']} a {new_stage} por {days_idle} dias inactivo"))
    return True, f"Tu mascota retrocedio a {new_stage} por {days_idle} dias sin cuidado."


def _remove_random_accessory(pet: dict) -> bool:
    """Quita un accesorio equipado aleatoriamente (para adultos inactivos)."""
    with get_conn() as conn:
        ph = "%s" if _USE_PG else "?"
        cur = _exec(conn,
                    f"SELECT id FROM pet_items WHERE pet_id={ph} AND equipped=1",
                    (pet["id"],))
        items = cur.fetchall() if hasattr(cur, "fetchall") else []
        if not items:
            return False
        import random
        victim = random.choice(items)
        iid = victim[0] if isinstance(victim, (list, tuple)) else victim["id"]
        _exec(conn, f"DELETE FROM pet_items WHERE id={ph}", (iid,))
    return True


def get_pet_items(pet_id: int) -> list[dict]:
    with get_conn() as conn:
        cur = _exec(conn,
                    "SELECT * FROM pet_items WHERE pet_id = ? ORDER BY purchased_at DESC",
                    (pet_id,))
        return _fetchall(cur)


def get_pet_log(pet_id: int, limit: int = 10) -> list[dict]:
    with get_conn() as conn:
        cur = _exec(conn,
                    "SELECT * FROM pet_actions_log WHERE pet_id = ? ORDER BY created_at DESC LIMIT ?",
                    (pet_id, limit))
        return _fetchall(cur)


# ── DECAIMIENTO DE HAMBRE ──────────────────────────────────────────────────

# Cuanto cae el hambre por hora (100 -> 0 en ~20 horas)
_HUNGER_DECAY_PER_HOUR = 5
# Cuanto cae la felicidad por hora cuando tiene hambre (<30)
_HAPPINESS_DECAY_PER_HOUR = 3


def decay_pet_hunger(user_id: int) -> None:
    """
    Calcula cuanto tiempo paso desde la ultima actualizacion de hambre
    y aplica el decaimiento. Llama al entrar al cuarto de la mascota.
    """
    with get_conn() as conn:
        ph = "%s" if _USE_PG else "?"
        cur = _exec(conn, f"SELECT * FROM pets WHERE user_id = {ph}", (user_id,))
        pet = _fetchone(cur)
        if not pet:
            return

        ref_str = pet.get("hunger_updated_at") or pet["last_activity"]
        try:
            ref_dt = datetime.fromisoformat(str(ref_str).split(".")[0])
        except (ValueError, TypeError):
            ref_dt = datetime.utcnow()

        hours_elapsed = (datetime.utcnow() - ref_dt).total_seconds() / 3600.0
        if hours_elapsed < 0.25:  # menos de 15 minutos -> ignorar
            return

        hunger_loss   = int(hours_elapsed * _HUNGER_DECAY_PER_HOUR)
        new_hunger    = max(0, pet["hunger"] - hunger_loss)

        # Felicidad cae si tuvo hambre
        happiness_loss = 0
        if new_hunger < 30:
            happiness_loss = int(hours_elapsed * _HAPPINESS_DECAY_PER_HOUR)
        new_happiness = max(0, pet["happiness"] - happiness_loss)

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        _exec(conn,
              f"""UPDATE pets SET hunger={ph}, happiness={ph},
                  hunger_updated_at={ph} WHERE id={ph}""",
              (new_hunger, new_happiness, now_str, pet["id"]))


# ── ESTADO EMOCIONAL ───────────────────────────────────────────────────────

def get_pet_emotion(pet: dict) -> str:
    """
    Retorna la emocion del pet basada en hunger y happiness.
    Valores: 'feliz' | 'neutral' | 'triste' | 'hambriento' | 'muriendo'
    """
    hunger    = pet.get("hunger", 100)
    happiness = pet.get("happiness", 100)

    if hunger < 5:
        return "muriendo"
    if hunger < 20:
        return "hambriento"
    if hunger < 40 or happiness < 30:
        return "triste"
    if hunger >= 60 and happiness >= 60:
        return "feliz"
    return "neutral"


_EMOTION_META = {
    "feliz":      {"label": "Feliz",      "color": "text-green-600",  "bg": "bg-green-50  border-green-200",  "anim": "bounce"},
    "neutral":    {"label": "Normal",     "color": "text-blue-500",   "bg": "bg-blue-50   border-blue-200",    "anim": "sway"},
    "triste":     {"label": "Triste",     "color": "text-yellow-600", "bg": "bg-yellow-50 border-yellow-200",  "anim": "droop"},
    "hambriento": {"label": "Hambriento", "color": "text-orange-500", "bg": "bg-orange-50 border-orange-200", "anim": "shake"},
    "muriendo":   {"label": "Muy mal!",   "color": "text-red-600",    "bg": "bg-red-50    border-red-200",     "anim": "shake"},
}


def get_emotion_meta(emotion: str) -> dict:
    return _EMOTION_META.get(emotion, _EMOTION_META["neutral"])


# ── RANKING DE MASCOTAS ────────────────────────────────────────────────────

def get_ranking_by_tienda(tienda: str) -> list[dict]:
    """
    Retorna lista de mascotas de la misma tienda, ordenadas por XP desc.
    Cada entrada incluye datos de la mascota + nombre/tienda del usuario.
    """
    with get_conn() as conn:
        cur = _exec(conn,
            """
            SELECT p.id, p.pet_name, p.animal_type, p.stage, p.xp, p.coins,
                   p.hunger, p.happiness,
                   u.name AS owner_name, u.tienda, u.id AS user_id
            FROM pets p
            JOIN users u ON u.id = p.user_id
            WHERE u.tienda = ?
            ORDER BY
              CASE p.stage
                WHEN 'adulto' THEN 4
                WHEN 'joven'  THEN 3
                WHEN 'bebe'   THEN 2
                ELSE 1
              END DESC,
              p.xp DESC
            """,
            (tienda,))
        return _fetchall(cur)

