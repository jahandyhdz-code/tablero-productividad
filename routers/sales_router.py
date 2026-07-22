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
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pet_functions as pets

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
    det      = user.get("determinante") or ""
    pres_t   = db.get_store_budget(det, year, month) if det else 0.0
    metrics  = db.get_productivity_metrics(user["id"], year, month)
    meta_row = db.get_user_meta(user["id"], year, month)
    plantilla   = meta_row["plantilla"] if meta_row else 0
    individual  = round(pres_t / max(plantilla, 1), 1) if pres_t and plantilla else 0
    return templates.TemplateResponse("dashboard.html", {
        "request":           request,
        "user":              user,
        "metrics":           metrics,
        "year":              year,
        "month":             month,
        "today":             date.today().isoformat(),
        "months_es":         MONTHS_ES,
        "meta":              meta_row,
        "individual":        individual,
        "presupuesto_tienda": pres_t,
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
    order_number: str = Form(""),
    amount_pesos: float = Form(0),
    almacen: str = Form(""),
    descripcion: str = Form(""),
):
    user = auth.get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    # ── Validacion numero de pedido ─────────────────────
    num = order_number.strip()
    error_msg = ""

    if num:
        ok, err = db.validate_order_number(num)
        if not ok:
            error_msg = err
        else:
            owner = db.get_order_number_owner(num)
            if owner:
                error_msg = (
                    f"El pedido {num} ya fue registrado "
                    f"por {owner['name']} (#{owner['associate_number']})."
                )

    if error_msg:
        metrics = db.get_productivity_metrics(user["id"], year, month)
        return _cards_and_history(
            request, metrics, user["id"], year, month, error=error_msg
        )

    total = round(gana_plus + kiosko, 2)
    if total <= 0:
        # Derivar tipo desde el numero de pedido (fallback seguro)
        if len(num) == 13:
            gana_plus, kiosko = 1.0, 0.0
        elif len(num) == 15:
            gana_plus, kiosko = 0.0, 1.0
        total = 1.0

    # Monto sin IVA (÷ 1.16)
    amount_sin_iva = round(amount_pesos / 1.16, 2) if amount_pesos > 0 else 0.0

    db.add_sales_entry(user["id"], entry_date, total,
                       gana_plus=gana_plus, kiosko=kiosko,
                       order_number=num, amount_sin_iva=amount_sin_iva,
                       almacen=almacen, descripcion=descripcion)

    # Monedas Tamagotchi: KIOSCO +2, GANA+ +3
    coins_earned = int(kiosko > 0) * pets.COINS_KIOSCO + int(gana_plus > 0) * pets.COINS_GANA
    if coins_earned > 0:
        pets.award_coins(user["id"], coins_earned, f"Venta: kiosko={kiosko} gana={gana_plus}")

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


@router.get("/sales/{entry_id}/edit", response_class=HTMLResponse)
async def edit_sale_form(request: Request, entry_id: int):
    """Devuelve el formulario de edición como un <tr> para HTMX swap."""
    user = auth.get_current_user(request)
    if not user:
        return HTMLResponse(status_code=401)
    today = date.today()
    year  = int(request.query_params.get("year", today.year))
    month = int(request.query_params.get("month", today.month))
    entry = db.get_sales_entry(entry_id, user["id"])
    if not entry:
        return HTMLResponse("<tr><td colspan='5'>No encontrado</td></tr>")
    return templates.TemplateResponse(
        "partials/edit_sale_row.html",
        {"request": request, "e": entry, "year": year, "month": month},
    )


@router.put("/sales/{entry_id}", response_class=HTMLResponse)
async def update_sale(
    request: Request,
    entry_id: int,
    gana_plus: float = Form(0),
    kiosko: float    = Form(0),
    year: int        = Form(...),
    month: int       = Form(...),
):
    """Guarda los cambios editados y refresca cards + historial."""
    user = auth.get_current_user(request)
    if not user:
        return HTMLResponse(status_code=401)
    db.update_sales_entry(entry_id, user["id"], gana_plus, kiosko)
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
    motiv   = db.get_motivational_message(user["id"], year, month)

    # Devuelve cards + calendário actualizados (OOB swap)
    cards_html = templates.TemplateResponse(
        "partials/productivity_cards.html",
        {"request": request, "metrics": metrics,
         "year": year, "month": month, "motiv": motiv},
    ).body.decode()

    cal_html = templates.TemplateResponse(
        "partials/rest_calendar.html",
        {"request": request, "metrics": metrics, "year": year, "month": month},
    ).body.decode()
    cal_oob = cal_html.replace(
        'id="rest-calendar"', 'id="rest-calendar" hx-swap-oob="outerHTML"', 1
    )
    return HTMLResponse(content=cards_html + cal_oob)
 

# ── CONCENTRADO DE VENTAS ────────────────────────────────────────────────────

@router.get("/concentrado", response_class=HTMLResponse)
async def concentrado(request: Request):
    user = auth.get_current_user(request)
    if not user:
        return HTMLResponse(status_code=401)

    today = date.today()
    year  = int(request.query_params.get("year",  today.year))
    month = int(request.query_params.get("month", today.month))

    tienda = user.get("tienda", "")
    if not tienda:
        return HTMLResponse(
            '<p class="text-gray-400 text-sm text-center py-12">'
            'Tu usuario no tiene tienda asignada.</p>'
        )

    data = db.get_concentrado_tienda(tienda, year, month)

    return templates.TemplateResponse("partials/concentrado.html", {
        "request":    request,
        "data":       data,
        "tienda":     tienda,
        "year":       year,
        "month":      month,
        "months_es":  MONTHS_ES,
        "me":         user["associate_number"],
    })


@router.delete("/concentrado/entry/{entry_id}", response_class=HTMLResponse)
async def concentrado_delete_entry(request: Request, entry_id: int):
    """Elimina una entrada propia y devuelve el concentrado actualizado."""
    user = auth.get_current_user(request)
    if not user:
        return HTMLResponse(status_code=401)

    today = date.today()
    year  = int(request.query_params.get("year",  today.year))
    month = int(request.query_params.get("month", today.month))

    db.delete_sales_entry(entry_id, user["id"])  # solo borra si es del usuario

    tienda = user.get("tienda", "")
    data   = db.get_concentrado_tienda(tienda, year, month)
    return templates.TemplateResponse("partials/concentrado.html", {
        "request":   request,
        "data":      data,
        "tienda":    tienda,
        "year":      year,
        "month":     month,
        "months_es": MONTHS_ES,
        "me":        user["associate_number"],
    })


@router.get("/concentrado/entry/{entry_id}/edit", response_class=HTMLResponse)
async def concentrado_edit_form(request: Request, entry_id: int):
    """Devuelve las celdas editables de No. Pedido y Monto para una fila propia."""
    user = auth.get_current_user(request)
    if not user:
        return HTMLResponse(status_code=401)
    year  = int(request.query_params.get("year",  date.today().year))
    month = int(request.query_params.get("month", date.today().month))

    # Busca la entrada (solo puede editar las propias)
    entry = db.get_sales_entry_by_owner(entry_id, user["id"])

    if not entry:
        return HTMLResponse(status_code=403)

    amount_con_iva = round((entry["amount_sin_iva"] or 0) * 1.16, 2)
    return templates.TemplateResponse("partials/concentrado_edit_row.html", {
        "request": request,
        "e":       entry,
        "amount_con_iva": amount_con_iva,
        "year":    year,
        "month":   month,
    })


@router.put("/concentrado/entry/{entry_id}", response_class=HTMLResponse)
async def concentrado_save_edit(
    request: Request,
    entry_id: int,
    order_number: str  = Form(""),
    amount_pesos: float = Form(0),
    year:  int = Form(...),
    month: int = Form(...),
):
    """Guarda la correccion de No. Pedido y Monto de una entrada propia."""
    user = auth.get_current_user(request)
    if not user:
        return HTMLResponse(status_code=401)

    amount_sin_iva = round(amount_pesos / 1.16, 2) if amount_pesos > 0 else 0.0
    db.update_entry_order_and_amount(
        entry_id, user["id"], order_number, amount_sin_iva
    )

    # Recarga el concentrado completo
    tienda = user.get("tienda", "")
    data   = db.get_concentrado_tienda(tienda, year, month)
    return templates.TemplateResponse("partials/concentrado.html", {
        "request":   request,
        "data":      data,
        "tienda":    tienda,
        "year":      year,
        "month":     month,
        "months_es": MONTHS_ES,
        "me":        user["associate_number"],
    })


@router.post("/concentrado/status/{entry_id}", response_class=HTMLResponse)
async def update_concentrado_status(
    request:  Request,
    entry_id: int,
    status:   str = Form(...),
    year:     int = Form(...),
    month:    int = Form(...),
):
    """Persiste el estatus, ajusta monedas de mascota y devuelve concentrado fresco."""
    user = auth.get_current_user(request)
    if not user:
        return HTMLResponse(status_code=401)
    tienda = user.get("tienda", "")

    _BAD = {"cancelado", "devolucion"}

    # Leer estado anterior antes de cambiar
    entry = db.get_entry_by_tienda(entry_id, tienda)
    if entry:
        old_status = entry["status"] or "pendiente"
        db.update_entry_status(entry_id, tienda, status)

        # Determinar monedas según canal del pedido
        if int(entry["units_gana_plus"] or 0) > 0:
            coins = pets.COINS_GANA
        else:
            coins = pets.COINS_KIOSCO

        # Cancelado/devolucion: descontar monedas (puede quedar negativo = deuda)
        if status in _BAD and old_status not in _BAD:
            pets.award_coins(entry["user_id"], -coins,
                             f"Descuento: pedido {entry_id} marcado como {status}")
        # Revertir a activo: restaurar monedas
        elif old_status in _BAD and status not in _BAD:
            pets.award_coins(entry["user_id"], coins,
                             f"Restauracion: pedido {entry_id} cambiado a {status}")

    # Devolver el concentrado actualizado completo
    data = db.get_concentrado_tienda(tienda, year, month)
    return templates.TemplateResponse("partials/concentrado.html", {
        "request":   request,
        "data":      data,
        "tienda":    tienda,
        "year":      year,
        "month":     month,
        "months_es": MONTHS_ES,
        "me":        user["associate_number"],
    })


# ── META MENSUAL + PLANTILLA ────────────────────────
@router.post("/meta", response_class=HTMLResponse)
async def set_meta(
    request: Request,
    plantilla: int = Form(...),
    year:      int = Form(...),
    month:     int = Form(...),
):
    user = auth.get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    # Presupuesto viene de store_budgets (no del form)
    det    = user.get("determinante") or ""
    pres_t = db.get_store_budget(det, year, month) if det else 0.0

    individual = db.set_user_meta(user["id"], year, month, pres_t, plantilla)
    metrics    = db.get_productivity_metrics(user["id"], year, month)
    meta_row   = db.get_user_meta(user["id"], year, month)
    motiv      = db.get_motivational_message(user["id"], year, month)

    cards_html = templates.TemplateResponse(
        "partials/productivity_cards.html",
        {"request": request, "metrics": metrics,
         "year": year, "month": month, "motiv": motiv},
    ).body.decode()

    meta_html = templates.TemplateResponse(
        "partials/meta_panel.html",
        {"request": request, "meta": meta_row,
         "individual": individual, "year": year, "month": month,
         "presupuesto_tienda": pres_t},
    ).body.decode()
    meta_oob = meta_html.replace(
        'id="meta-panel"', 'id="meta-panel" hx-swap-oob="outerHTML"', 1
    )
    return HTMLResponse(content=cards_html + meta_oob)


# ── HELPERS HTML ─────────────────────────────────────────

def _cards_and_history(request, metrics, user_id, year, month, error: str = ""):
    # Mensaje motivador
    motiv = db.get_motivational_message(user_id, year, month)

    cards_html = templates.TemplateResponse(
        "partials/productivity_cards.html",
        {"request": request, "metrics": metrics,
         "year": year, "month": month, "motiv": motiv},
    ).body.decode()

    # Error OOB
    error_oob = (
        f'<div id="sale-error" hx-swap-oob="innerHTML">'
        f'<p class="text-red-600 text-xs font-semibold bg-red-50 border border-red-200 '
        f'rounded-xl px-3 py-2">{error}</p></div>'
        if error else
        '<div id="sale-error" hx-swap-oob="innerHTML"></div>'
    )

    return HTMLResponse(content=cards_html + error_oob)
