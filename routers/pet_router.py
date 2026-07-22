"""
routers/pet_router.py — Tamagotchi de productividad.
"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import auth
import pet_functions as pets
import pet_art
import database as db

router = APIRouter(prefix="/mascota", tags=["mascota"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

ANIMALS = [
    {"id": "perro",   "nombre": "Perro",   "desc": "Leal y jugueton"},
    {"id": "gato",    "nombre": "Gato",    "desc": "Misterioso e independiente"},
    {"id": "conejo",  "nombre": "Conejo",  "desc": "Tierno y veloz"},
    {"id": "pollito", "nombre": "Pollito", "desc": "Alegre y curioso"},
    {"id": "oso",     "nombre": "Oso",     "desc": "Fuerte y protector"},
    {"id": "dragon",  "nombre": "Dragon",  "desc": "Magico y poderoso"},
]

# Huevos de cada animal para la pantalla de seleccion
EGGS_SVG = {a["id"]: pet_art.get_art(a["id"], "huevo") for a in ANIMALS}


def _get_user_or_redirect(request: Request):
    user = auth.get_current_user(request)
    if not user:
        return None, RedirectResponse("/login", status_code=302)
    return user, None


def _pet_context(pet: dict, items: list, log: list, msg: str = "") -> dict:
    """Contexto comun para las dos rutas que renderizan la mascota."""
    equipped  = [i["item_type"] for i in items if i["equipped"]]
    xp_needed = pets.PET_STAGE_XP.get(pet["stage"], 1)
    xp_pct    = min(100, int(pet["xp"] / xp_needed * 100)) if xp_needed else 100
    pet_svg   = pet_art.get_art(pet["animal_type"], pet["stage"])
    emotion   = pets.get_pet_emotion(pet)
    emeta     = pets.get_emotion_meta(emotion)
    return {
        "pet":       pet,
        "items":     items,
        "equipped":  equipped,
        "log":       log,
        "catalog":   pets.PET_ITEMS_CATALOG,
        "xp_pct":    xp_pct,
        "xp_needed": xp_needed,
        "stages":    pets.PET_STAGES,
        "pet_svg":   pet_svg,
        "msg":       msg,
        "emotion":   emotion,
        "emeta":     emeta,
    }


def _calc_retro_coins(user_id: int) -> tuple[int, int]:
    """
    Calcula monedas retroactivas pendientes.
    Retorna (coins_a_otorgar, num_entradas).
    Solo otorga si nunca hubo un log de tipo 'earn_coins' con razon 'retro'.
    """
    pet = pets.get_pet_by_user(user_id)
    if not pet:
        return 0, 0

    # Ver si ya hubo pago retro
    log_all = pets.get_pet_log(pet["id"], limit=100)
    ya_retro = any(
        (e.get("action") == "earn_coins" and "retro" in (e.get("detail") or ""))
        for e in log_all
    )
    if ya_retro:
        return 0, 0

    entries = db.get_all_sales_entries(user_id)
    retro = sum(
        (pets.COINS_KIOSCO if (e.get("units_kiosko") or 0) > 0 else 0)
        + (pets.COINS_GANA  if (e.get("units_gana_plus") or 0) > 0 else 0)
        for e in entries
    )
    return retro, len(entries)


# ── RUTAS ───────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def pet_home(request: Request):
    user, redir = _get_user_or_redirect(request)
    if redir:
        return redir

    pets.check_pet_regression(user["id"])
    pets.decay_pet_hunger(user["id"])   # << decaimiento de hambre

    pet = pets.get_pet_by_user(user["id"])
    if not pet:
        return RedirectResponse("/mascota/escoger", status_code=302)

    # Monedas retroactivas: se otorgan automaticamente la primera vez
    retro, n_entries = _calc_retro_coins(user["id"])
    msg = request.query_params.get("msg", "")
    if retro > 0:
        pets.award_coins(user["id"], retro,
                         f"retro: {retro} monedas por {n_entries} ventas anteriores")
        pet = pets.get_pet_by_user(user["id"])          # recargar con monedas nuevas
        if not msg:
            msg = f"Se acreditaron {retro} monedas por tus ventas anteriores!"

    items = pets.get_pet_items(pet["id"])
    log   = pets.get_pet_log(pet["id"], limit=8)

    # Top 3 ranking de la tienda para mostrar en la pagina
    from datetime import date as _date
    _hoy = _date.today()
    det     = user.get("determinante") or ""
    ranking = pets.get_ranking_by_tienda(det, _hoy.year, _hoy.month)[:3]
    for i, r in enumerate(ranking):
        r["rank"]    = i + 1
        r["is_mine"] = (r["user_id"] == user["id"])

    return templates.TemplateResponse("pet.html", {
        "request": request,
        "user":    user,
        "ranking": ranking,
        **_pet_context(pet, items, log, msg),
    })


@router.get("/escoger", response_class=HTMLResponse)
async def choose_pet_page(request: Request):
    user, redir = _get_user_or_redirect(request)
    if redir:
        return redir
    if pets.get_pet_by_user(user["id"]):
        return RedirectResponse("/mascota", status_code=302)
    return templates.TemplateResponse("choose_pet.html", {
        "request":   request,
        "user":      user,
        "animals":   ANIMALS,
        "eggs_svg":  EGGS_SVG,
    })


@router.post("/escoger", response_class=HTMLResponse)
async def choose_pet_submit(
    request: Request,
    animal_type: str = Form(...),
    pet_name:    str = Form(...),
):
    user, redir = _get_user_or_redirect(request)
    if redir:
        return redir
    if pets.get_pet_by_user(user["id"]):
        return RedirectResponse("/mascota", status_code=302)
    if animal_type not in [a["id"] for a in ANIMALS]:
        return RedirectResponse("/mascota/escoger", status_code=302)

    name = pet_name.strip()[:30] or "Mi Mascota"
    pets.create_pet(user["id"], animal_type, name)

    # Monedas retroactivas al crear (se vuelven a calcular en pet_home si fallan aqui)
    entries = db.get_all_sales_entries(user["id"])
    retro = sum(
        (pets.COINS_KIOSCO if (e.get("units_kiosko") or 0) > 0 else 0)
        + (pets.COINS_GANA  if (e.get("units_gana_plus") or 0) > 0 else 0)
        for e in entries
    )
    if retro > 0:
        pets.award_coins(user["id"], retro,
                         f"retro: {retro} monedas por {len(entries)} ventas anteriores")

    return RedirectResponse("/mascota?msg=Bienvenido+a+tu+nueva+mascota!", status_code=302)


@router.post("/usar/{item_type}", response_class=HTMLResponse)
async def use_item(request: Request, item_type: str):
    user, redir = _get_user_or_redirect(request)
    if redir:
        return redir
    ok, msg, pet = pets.feed_pet(user["id"], item_type)
    if not pet:
        return RedirectResponse("/mascota/escoger", status_code=302)

    items = pets.get_pet_items(pet["id"])
    log   = pets.get_pet_log(pet["id"], limit=8)

    return templates.TemplateResponse("partials/pet_status.html", {
        "request": request,
        "user":    user,
        "ok":      ok,
        **_pet_context(pet, items, log, msg),
    })


# ── RANKING ──────────────────────────────────────────────────────

@router.get("/ranking", response_class=HTMLResponse)
async def pet_ranking(request: Request):
    user, redir = _get_user_or_redirect(request)
    if redir:
        return redir

    from datetime import date as _date
    today = _date.today()
    year  = int(request.query_params.get("year",  today.year))
    month = int(request.query_params.get("month", today.month))

    det    = user.get("determinante") or ""
    tienda = user.get("tienda", "")
    ranking = pets.get_ranking_by_tienda(det, year, month)
    my_pet  = pets.get_pet_by_user(user["id"])

    # Enriquecer con art SVG y emocion
    for i, r in enumerate(ranking):
        r["rank"]    = i + 1
        r["pet_svg"] = pet_art.get_art(r["animal_type"], r["stage"])
        r["emotion"] = pets.get_pet_emotion(r)
        r["emeta"]   = pets.get_emotion_meta(r["emotion"])
        r["is_mine"] = (r["user_id"] == user["id"])

    return templates.TemplateResponse("pet_ranking.html", {
        "request": request,
        "user":    user,
        "ranking": ranking,
        "my_pet":  my_pet,
        "tienda":  tienda,
        "year":    year,
        "month":   month,
    })


# ── MINIJUEGO ──────────────────────────────────────────────────────────────────────

@router.get("/jugar", response_class=HTMLResponse)
async def minijuego_page(request: Request):
    user, redir = _get_user_or_redirect(request)
    if redir:
        return redir

    pet = pets.get_pet_by_user(user["id"])
    if not pet:
        return RedirectResponse("/mascota/escoger", status_code=302)

    plays_today = pets.get_plays_today(pet["id"])
    plays_left  = max(0, pets.MAX_PLAYS_PER_DAY - plays_today)

    return templates.TemplateResponse("pet_minijuego.html", {
        "request":    request,
        "user":       user,
        "pet":        pet,
        "plays_left": plays_left,
        "max_plays":  pets.MAX_PLAYS_PER_DAY,
        "max_score":  pets.MAX_GAME_SCORE,
    })


@router.post("/jugar", response_class=HTMLResponse)
async def minijuego_submit(request: Request, score: int = Form(...)):
    user, redir = _get_user_or_redirect(request)
    if redir:
        return redir

    ok, msg, pet = pets.record_minijuego(user["id"], score)
    if not pet:
        return RedirectResponse("/mascota/escoger", status_code=302)

    plays_today = pets.get_plays_today(pet["id"])
    plays_left  = max(0, pets.MAX_PLAYS_PER_DAY - plays_today)

    return templates.TemplateResponse("partials/minijuego_result.html", {
        "request":    request,
        "user":       user,
        "pet":        pet,
        "ok":         ok,
        "msg":        msg,
        "plays_left": plays_left,
        "max_plays":  pets.MAX_PLAYS_PER_DAY,
        "score":      score,
        "max_score":  pets.MAX_GAME_SCORE,
    })
