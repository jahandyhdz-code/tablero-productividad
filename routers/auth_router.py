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

_EMPTY_FORM = {"associate_number": "", "name": "", "tienda": "", "determinante": "", "squad": "", "distrito": ""}


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
    """Pagina de auto-registro."""
    if auth.get_current_user(request):
        return RedirectResponse("/", status_code=302)
    from tiendas_catalogo import TIENDAS
    from routers.admin_router import SQUADS, DISTRITOS
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": None,
         "catalogo_tiendas": TIENDAS,
         "squads": SQUADS, "distritos": DISTRITOS,
         "form": _EMPTY_FORM},
    )


@router.post("/registro", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    associate_number: str = Form(...),
    name: str = Form(...),
    determinante: str = Form(...),
    squad: str = Form(default=""),
    distrito: str = Form(default=""),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    from tiendas_catalogo import TIENDAS, TIENDAS_BY_DET
    from routers.admin_router import SQUADS, DISTRITOS
    form = {"associate_number": associate_number.strip(),
            "name": name.strip(),
            "determinante": determinante.strip(),
            "squad": squad.strip(),
            "distrito": distrito.strip()}

    def err(msg: str):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": msg,
             "catalogo_tiendas": TIENDAS,
             "squads": SQUADS, "distritos": DISTRITOS,
             "form": form},
            status_code=400,
        )

    det = determinante.strip()
    tienda_nombre = TIENDAS_BY_DET.get(det, "")

    if not form["associate_number"].isdigit():
        return err("El numero de asociado solo debe contener digitos.")
    if len(form["name"]) < 3:
        return err("Ingresa tu nombre completo.")
    if not tienda_nombre:
        return err("Selecciona una tienda valida. Escribe el numero de determinante o el nombre.")
    if len(password) < 6:
        return err("La contrasena debe tener al menos 6 caracteres.")
    if password != confirm_password:
        return err("Las contrasenas no coinciden.")
    if db.associate_number_exists(form["associate_number"]):
        return err("Ese numero de asociado ya esta registrado. Ve a Ingresar e introduce tu contrasena.")

    pwd_hash = auth.hash_password(password)
    user_id  = db.create_user(
        associate_number=form["associate_number"],
        name=form["name"],
        password_hash=pwd_hash,
        role="user",
        tienda=tienda_nombre,
        must_change_password=0,
    )
    db.update_user_determinante(user_id, det)
    if squad.strip() or distrito.strip():
        db.update_user_squad_distrito(user_id, squad.strip(), distrito.strip())

    # Crear sesion y entrar directo
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
