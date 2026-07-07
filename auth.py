"""
auth.py — Password hashing y helpers de sesión para FastAPI.
"""
import secrets
import bcrypt
from fastapi import Request, HTTPException, status
import database as db

COOKIE_NAME = "vp_session"


# ─────────────────────────────────────────────────────────
#  PASSWORD
# ─────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ─────────────────────────────────────────────────────────
#  SESSION
# ─────────────────────────────────────────────────────────

def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    db.create_session(token, user_id)
    return token


def get_current_user(request: Request) -> dict | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    session = db.get_session(token)
    if not session:
        return None
    return db.get_user_by_id(session["user_id"])


def require_auth(request: Request) -> dict:
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"},
        )
    return user


def require_admin(request: Request) -> dict:
    user = require_auth(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    return user


def seed_admin_if_empty():
    """Crea un admin por defecto si no hay usuarios (sin forzar cambio de pwd)."""
    users = db.get_all_users()
    if not users:
        uid = db.create_user(
            associate_number="000000",
            name="Administrador",
            password_hash=hash_password("Admin2024!"),
            role="admin",
        )
        # El admin inicial conoce su contrasena; no forzamos cambio
        with db.get_conn() as conn:
            db._exec(conn, "UPDATE users SET must_change_password=0 WHERE id=?", (uid,))
        print(" Admin creado — asociado: 000000 | contrasena: Admin2024!")
