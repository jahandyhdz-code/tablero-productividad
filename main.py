"""
main.py — FastAPI entry point para el sistema de Productividad de Ventas.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import database as db
import auth
from routers import auth_router, sales_router, admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    db.run_migrations()
    auth.seed_admin_if_empty()
    yield


app = FastAPI(title="Productividad de Ventas", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

app.include_router(auth_router.router)
app.include_router(sales_router.router)
app.include_router(admin_router.router)
