"""
routers/sales_router.py — Registro de ventas y días de descanso del asociado.
"""
from datetime import date
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import auth
import database as db

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

MONTHS_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def _period(request: Request) -> tuple[int, int]:
    today = date.today()
    return (
        int(request.query_params.get("year", today.year)),
        int(request.query_params.get("month", today.month)),
    )


def _render_dashboard(request: Request, user: dict, year: int, month: int):
    metrics = db.get_productivity_metrics(user["id"], year, month)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "metrics": metrics,
        "year": year,
        "month": month,
        "today": date.today().isoformat(),
        "months_es": MONTHS_ES,
    })


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = auth.get_current_user(request)
    if not user:
        return RedirectResponse("/bienvenido", status_code=302)
    if user.get("must_change_password"):
        return RedirectResponse("/cambiar-contrasena", status_code=302)
    if user["role"] == "admin":
        return RedirectResponse("/admin", status_code=302)
    year, month = _period(request)
    return _render_dashboard(request, user, year, month)


# ── VENTAS ──────────────────────────────────────────────

@router.post("/sales", response_class=HTMLResponse)
async def add_sale(
    request: Request,
    entry_date: str = Form(...),
    gana_plus: float = Form(0),
    kiosko: float = Form(0),
    year: int = Form(...),
    month: int = Form(...),
):
    user = auth.get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    total = round(gana_plus + kiosko, 2)
    if total <= 0:
        # Nada que guardar — devuelve las cards sin cambio
        metrics = db.get_productivity_metrics(user["id"], year, month)
        return _cards_and_history(request, metrics, user["id"], year, month)

    db.add_sales_entry(user["id"], entry_date, total, gana_plus=gana_plus, kiosko=kiosko)
    metrics = db.get_productivity_metrics(user["id"], year, month)
    return _cards_and_history(request, metrics, user["id"], year, month)


@router.delete("/sales/{entry_id}", response_class=HTMLResponse)
async def delete_sale(request: Request, entry_id: int):
    user = auth.get_current_user(request)
    if not user:
        return HTMLResponse(status_code=401)
    today = date.today()
    year  = int(request.query_params.get("year", today.year))
    month = int(request.query_params.get("month", today.month))
    db.delete_sales_entry(entry_id, user["id"])
    metrics = db.get_productivity_metrics(user["id"], year, month)
    return _cards_and_history(request, metrics, user["id"], year, month)


# ── DÍAS DE DESCANSO ────────────────────────────────────

@router.post("/rest-days/{rest_date}", response_class=HTMLResponse)
async def toggle_rest_day(request: Request, rest_date: str):
    user = auth.get_current_user(request)
    if not user:
        return HTMLResponse(status_code=401)

    db.toggle_rest_day(user["id"], rest_date)

    today = date.today()
    year  = int(request.query_params.get("year", today.year))
    month = int(request.query_params.get("month", today.month))
    metrics = db.get_productivity_metrics(user["id"], year, month)

    # Devuelve cards + calendário actualizados (OOB swap)
    cards_html = templates.TemplateResponse(
        "partials/productivity_cards.html",
        {"request": request, "metrics": metrics, "year": year, "month": month},
    ).body.decode()

    cal_html = templates.TemplateResponse(
        "partials/rest_calendar.html",
        {"request": request, "metrics": metrics, "year": year, "month": month},
    ).body.decode()
    cal_oob = cal_html.replace(
        'id="rest-calendar"', 'id="rest-calendar" hx-swap-oob="outerHTML"', 1
    )
    return HTMLResponse(content=cards_html + cal_oob)


# ── HELPERS HTML ─────────────────────────────────────────

def _cards_and_history(request, metrics, user_id, year, month):
    cards_html = templates.TemplateResponse(
        "partials/productivity_cards.html",
        {"request": request, "metrics": metrics, "year": year, "month": month},
    ).body.decode()

    history_html = templates.TemplateResponse(
        "partials/sales_history.html",
        {"request": request, "entries": metrics["entries"],
         "user_id": user_id, "year": year, "month": month},
    ).body.decode()

    history_oob = history_html.replace(
        'id="history-body"', 'id="history-body" hx-swap-oob="innerHTML"', 1
    )
    return HTMLResponse(content=cards_html + history_oob)
