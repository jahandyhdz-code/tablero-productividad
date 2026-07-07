"""
routers/auth_router.py — Login, logout, registro público y cambio de contraseña.
"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import auth
import database as db

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

_EMPTY_FORM = {"associate_number": "", "name": "", "tienda": ""}


@router.get("/bienvenido", response_class=HTMLResponse)
async def welcome_page(request: Request):
    """Página de bienvenida — muestra las dos opciones: Ingresar o Registrarse."""
    user = auth.get_current_user(request)
    if user:
        if user.get("must_change_password"):
            return RedirectResponse("/cambiar-contrasena", status_code=302)
        return RedirectResponse("/admin" if user["role"] == "admin" else "/", status_code=302)
    return templates.TemplateResponse("welcome.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if auth.get_current_user(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    associate_number: str = Form(...),
    password: str = Form(...),
):
    user = db.get_user_by_associate(associate_number)
    if not user or not auth.verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Número de asociado o contraseña incorrectos."},
            status_code=401,
        )

    token = auth.create_session(user["id"])
    # Si debe cambiar contraseña, redirige antes de dar acceso real
    dest = "/cambiar-contrasena" if user.get("must_change_password") else "/"
    if user["role"] == "admin" and not user.get("must_change_password"):
        dest = "/admin"

    resp = RedirectResponse(dest, status_code=302)
    resp.set_cookie(auth.COOKIE_NAME, token, httponly=True, samesite="lax", max_age=28800)
    return resp


@router.get("/cambiar-contrasena", response_class=HTMLResponse)
async def change_password_page(request: Request):
    user = auth.get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(
        "change_password.html", {"request": request, "user": user, "error": None, "ok": False}
    )


@router.post("/cambiar-contrasena", response_class=HTMLResponse)
async def change_password_submit(
    request: Request,
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    user = auth.get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    if len(new_password) < 6:
        return templates.TemplateResponse(
            "change_password.html",
            {"request": request, "user": user,
             "error": "La contraseña debe tener al menos 6 caracteres.", "ok": False},
        )
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "change_password.html",
            {"request": request, "user": user,
             "error": "Las contraseñas no coinciden.", "ok": False},
        )

    db.update_user_password(user["id"], auth.hash_password(new_password), clear_force=True)

    dest = "/admin" if user["role"] == "admin" else "/"
    return RedirectResponse(dest, status_code=302)


# ── Registro público ────────────────────────────────────────────────────────

@router.get("/registro", response_class=HTMLResponse)
async def register_page(request: Request):
    """Página de auto-registro — pública, sin autenticación requerida."""
    if auth.get_current_user(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": None,
         "tiendas": db.DETERMINANTES, "form": _EMPTY_FORM},
    )


@router.post("/registro", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    associate_number: str = Form(...),
    name: str = Form(...),
    tienda: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    form = {"associate_number": associate_number.strip(),
            "name": name.strip(), "tienda": tienda.strip()}

    def err(msg: str):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": msg,
             "tiendas": db.DETERMINANTES, "form": form},
            status_code=400,
        )

    # Validaciones
    if not form["associate_number"].isdigit():
        return err("El número de asociado solo debe contener dígitos.")
    if len(form["name"]) < 3:
        return err("Ingresa tu nombre completo.")
    if tienda not in db.DETERMINANTES:
        return err("Selecciona una tienda válida de la lista.")
    if len(password) < 6:
        return err("La contraseña debe tener al menos 6 caracteres.")
    if password != confirm_password:
        return err("Las contraseñas no coinciden.")
    if db.associate_number_exists(form["associate_number"]):
        return err("Ese número de asociado ya está registrado. Ve a Ingresar e introduce tu contraseña.")

    # Crear usuario — contraseña elegida por él, sin forzar cambio
    pwd_hash = auth.hash_password(password)
    user_id  = db.create_user(
        associate_number=form["associate_number"],
        name=form["name"],
        password_hash=pwd_hash,
        role="user",
        tienda=form["tienda"],
        must_change_password=0,
    )

    # Crear sesión y entrar directo
    token = auth.create_session(user_id)
    resp  = RedirectResponse("/", status_code=302)
    resp.set_cookie(auth.COOKIE_NAME, token, httponly=True, samesite="lax", max_age=28800)
    return resp


@router.post("/logout")
async def logout(request: Request):
    token = request.cookies.get(auth.COOKIE_NAME)
    if token:
        db.delete_session(token)
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie(auth.COOKIE_NAME)
    return resp
