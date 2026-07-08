"""
routers/admin_router.py — Panel de administración: usuarios, metas de equipo.
"""
import io
from datetime import date
from typing import List
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import auth
import database as db

# ── Colores Walmart ──────────────────────────────────────
_BLUE      = "FF0071CE"   # Walmart Blue
_DARK_BLUE = "FF004C99"   # Dark Navy
_YELLOW    = "FFFFC220"   # Spark Yellow
_WHITE     = "FFFFFFFF"
_LIGHT     = "FFF5F8FC"   # fila alterna
_GREEN     = "FF00A651"
_RED       = "FFCC0000"
_ORANGE    = "FFFF6A00"
_AMBER     = "FFFFC107"


def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def _font(bold=False, color=None, size=11):
    return Font(bold=bold, color=color or "FF000000", size=size)


def _thin_border() -> Border:
    side = Side(style="thin", color="FFD0D7E2")
    return Border(left=side, right=side, top=side, bottom=side)


def _badge_fill(pct: float) -> str:
    if pct >= 100:
        return _GREEN
    if pct >= 75:
        return _AMBER
    if pct >= 50:
        return _ORANGE
    return _RED


def _build_excel(year: int, month: int,
                 tiendas_filter: list | None = None) -> bytes:
    """Genera el workbook en memoria y devuelve los bytes .xlsx."""
    month_name = db.MONTHS_ES[month - 1]
    team    = db.get_team_productivity(year, month, tiendas_filter=tiendas_filter)
    entries = db.get_all_entries_for_month(year, month, tiendas_filter=tiendas_filter)

    wb = Workbook()

    # ── Hoja 1: Resumen del equipo ─────────────────────────
    ws1 = wb.active
    ws1.title = "Resumen"

    # Título
    ws1.merge_cells("A1:G1")
    ws1["A1"] = f"Productividad del Equipo — {month_name} {year}"
    ws1["A1"].font      = _font(bold=True, color=_WHITE, size=14)
    ws1["A1"].fill      = _fill(_DARK_BLUE)
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 32

    # Encabezados
    headers1 = ["#", "No. Asociado", "Nombre", "Tienda / Determinante",
                "Unidades Vendidas", "Meta Mensual", "% Alcance"]
    ws1.append(headers1)
    for col_idx, _ in enumerate(headers1, start=1):
        cell = ws1.cell(row=2, column=col_idx)
        cell.font      = _font(bold=True, color=_WHITE)
        cell.fill      = _fill(_BLUE)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border    = _thin_border()
    ws1.row_dimensions[2].height = 22

    # Datos
    for i, member in enumerate(team, start=1):
        row_num = i + 2
        alt_fill = _fill(_LIGHT) if i % 2 == 0 else _fill(_WHITE)
        pct_str  = f"{member['monthly_pct']}%" if member["monthly_target"] > 0 else "Sin meta"
        pct_fill = _fill(_badge_fill(member["monthly_pct"])) if member["monthly_target"] > 0 else _fill(_WHITE)
        row_data = [
            i,
            member["associate_number"],
            member["name"],
            member["tienda"] or "—",
            int(member["monthly_actual"]),
            int(member["monthly_target"]) if member["monthly_target"] > 0 else "—",
            pct_str,
        ]
        ws1.append(row_data)
        for col_idx, _ in enumerate(row_data, start=1):
            cell = ws1.cell(row=row_num, column=col_idx)
            cell.border    = _thin_border()
            cell.alignment = Alignment(horizontal="center" if col_idx in (1, 5, 6, 7) else "left",
                                       vertical="center")
            cell.fill = pct_fill if col_idx == 7 else alt_fill
            if col_idx == 7 and member["monthly_target"] > 0:
                cell.font = _font(bold=True, color=_WHITE)

    # Totales (fila final)
    total_row = len(team) + 3
    ws1.cell(total_row, 1).value  = ""
    ws1.cell(total_row, 3).value  = "TOTAL EQUIPO"
    ws1.cell(total_row, 3).font   = _font(bold=True)
    ws1.cell(total_row, 5).value  = sum(int(m["monthly_actual"]) for m in team)
    ws1.cell(total_row, 5).font   = _font(bold=True)
    ws1.cell(total_row, 6).value  = sum(int(m["monthly_target"]) for m in team if m["monthly_target"] > 0)
    ws1.cell(total_row, 6).font   = _font(bold=True)
    for col_idx in range(1, 8):
        ws1.cell(total_row, col_idx).fill   = _fill(_YELLOW)
        ws1.cell(total_row, col_idx).border = _thin_border()

    # Anchos de columna hoja 1
    for col, width in zip("ABCDEFG", [5, 14, 28, 30, 18, 14, 12]):
        ws1.column_dimensions[col].width = width

    # ── Hoja 2: Detalle de capturas ────────────────────────
    ws2 = wb.create_sheet("Detalle")
    ws2.merge_cells("A1:F1")
    ws2["A1"] = f"Detalle de Capturas — {month_name} {year}"
    ws2["A1"].font      = _font(bold=True, color=_WHITE, size=14)
    ws2["A1"].fill      = _fill(_DARK_BLUE)
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 32

    headers2 = ["No. Asociado", "Nombre", "Tienda / Determinante",
                "Fecha", "Unidades Vendidas", "Notas"]
    ws2.append(headers2)
    for col_idx, _ in enumerate(headers2, start=1):
        cell = ws2.cell(row=2, column=col_idx)
        cell.font      = _font(bold=True, color=_WHITE)
        cell.fill      = _fill(_BLUE)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border    = _thin_border()
    ws2.row_dimensions[2].height = 22

    for i, entry in enumerate(entries, start=1):
        row_num  = i + 2
        alt_fill = _fill(_LIGHT) if i % 2 == 0 else _fill(_WHITE)
        row_data = [
            entry["associate_number"],
            entry["name"],
            entry["tienda"] or "—",
            entry["entry_date"],
            int(entry["units_sold"]),
            entry["notes"] or "",
        ]
        ws2.append(row_data)
        for col_idx, _ in enumerate(row_data, start=1):
            cell = ws2.cell(row=row_num, column=col_idx)
            cell.fill      = alt_fill
            cell.border    = _thin_border()
            cell.alignment = Alignment(
                horizontal="center" if col_idx in (1, 4, 5) else "left",
                vertical="center",
            )

    for col, width in zip("ABCDEF", [14, 28, 30, 14, 18, 35]):
        ws2.column_dimensions[col].width = width

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

MONTHS_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def _admin_user(request: Request):
    user = auth.get_current_user(request)
    if not user or user["role"] != "admin":
        return None
    return user


def _tiendas_filter(user: dict) -> list | None:
    """Devuelve la lista de tiendas que puede ver este admin.
    None = sin restricción (super admin). Lista = solo esas tiendas.
    """
    tf = db.get_admin_tiendas(user["id"])
    return tf if tf else None


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = _admin_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    today = date.today()
    year  = int(request.query_params.get("year",  today.year))
    month = int(request.query_params.get("month", today.month))

    tf        = _tiendas_filter(user)
    team      = db.get_team_productivity(year, month, tiendas_filter=tf)
    all_users = db.get_all_users(tiendas_filter=tf)
    wk_start, wk_end = db.commercial_week(today)

    # Tiendas visibles para este admin (para el picker de crear usuario)
    tiendas_disp = tf if tf else db.DETERMINANTES

    top5 = [m for m in team if m["prod_mensual"] > 0][:5]

    return templates.TemplateResponse("admin.html", {
        "request":          request,
        "user":             user,
        "team":             team,
        "all_users":        all_users,
        "year":             year,
        "month":            month,
        "today":            today.isoformat(),
        "months_es":        MONTHS_ES,
        "determinantes":    tiendas_disp,
        "todas_las_tiendas": db.DETERMINANTES,
        "admin_tiendas":    tf or [],
        "is_super_admin":   tf is None,
        "msg":              request.query_params.get("msg"),
        "error":            request.query_params.get("error"),
        "top5":             top5,
        "wk_start":         wk_start.strftime("%d/%m"),
        "wk_end":           wk_end.strftime("%d/%m"),
        "daily_goal":       db.DAILY_GOAL,
    })


@router.post("/users", response_class=HTMLResponse)
async def create_user(
    request: Request,
    associate_number: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    admin_tiendas: List[str] = Form(default=[]),
):
    admin = _admin_user(request)
    if not admin:
        return RedirectResponse("/login", status_code=302)

    if db.associate_number_exists(associate_number):
        return RedirectResponse(
            f"/admin?error=El+número+{associate_number}+ya+existe", status_code=302
        )

    user_id = db.create_user(
        associate_number=associate_number,
        name=name,
        password_hash=auth.hash_password(password),
        role=role,
        tienda="",
    )
    # Si es admin, guardar las tiendas asignadas
    if role == "admin" and admin_tiendas:
        db.set_admin_tiendas(user_id, admin_tiendas)

    return RedirectResponse("/admin?msg=Usuario+creado+correctamente", status_code=302)


@router.post("/team-target", response_class=HTMLResponse)
async def set_team_target(
    request: Request,
    year: int = Form(...),
    month: int = Form(...),
    target_units: float = Form(...),
):
    """Asigna la misma meta a todo el equipo de un solo golpe."""
    if not _admin_user(request):
        return RedirectResponse("/login", status_code=302)

    # Solo aplica a los usuarios visibles para este admin
    admin = _admin_user(request)
    tf    = _tiendas_filter(admin)
    usuarios = db.get_all_users(tiendas_filter=tf)
    for u in usuarios:
        db.set_sales_target(u["id"], year, month, target_units)
    return RedirectResponse(
        f"/admin?year={year}&month={month}&msg=Meta+de+equipo+actualizada", status_code=302
    )


@router.post("/users/{user_id}/delete", response_class=HTMLResponse)
async def delete_user(request: Request, user_id: int):
    """Elimina un usuario y todos sus datos. No se puede borrar a uno mismo."""
    admin = _admin_user(request)
    if not admin:
        return RedirectResponse("/login", status_code=302)
    if admin["id"] == user_id:
        return RedirectResponse("/admin?error=No+puedes+eliminar+tu+propia+cuenta", status_code=302)
    target = db.get_user_by_id(user_id)
    if not target:
        return RedirectResponse("/admin?error=Usuario+no+encontrado", status_code=302)
    db.delete_user(user_id)
    nombre = target["name"]
    return RedirectResponse(f"/admin?msg=Usuario+{nombre}+eliminado+correctamente", status_code=302)


@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password(
    request: Request,
    user_id: int = Form(...),
    new_password: str = Form(...),
):
    if not _admin_user(request):
        return RedirectResponse("/login", status_code=302)

    # Actualiza la contrasena directamente — el asociado entra sin friccion
    db.update_user_password(user_id, auth.hash_password(new_password), clear_force=True)
    return RedirectResponse("/admin?msg=Contrasena+restablecida+correctamente", status_code=302)


@router.get("/export/excel")
async def export_excel(request: Request):
    """Descarga el reporte del equipo en formato .xlsx."""
    user = _admin_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    today = date.today()
    year  = int(request.query_params.get("year",  today.year))
    month = int(request.query_params.get("month", today.month))
    month_name = MONTHS_ES[month - 1]

    tf         = _tiendas_filter(user)
    xlsx_bytes = _build_excel(year, month, tiendas_filter=tf)
    filename   = f"productividad_{month_name.lower()}_{year}.xlsx"

    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
