"""
main.py — FastAPI entry point para el sistema de Productividad de Ventas.
"""
import io
import os
import socket
import tempfile
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import database as db
import auth
from routers import auth_router, sales_router, admin_router, pet_router


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
app.include_router(pet_router.router)


def _local_ip() -> str:
    """Obtiene la IP LAN del equipo (sin salir a internet)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


@app.get("/qr", response_class=HTMLResponse, include_in_schema=False)
async def qr_page():
    """Pagina con QR para abrir el sistema desde un celular en la misma red."""
    import segno

    ip   = _local_ip()
    url  = f"http://{ip}:8002"
    port = 8002

    # segno escribe a archivo; usamos tempfile para evitar problemas de codecs
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        qr = segno.make(url, error="m")
        qr.save(tmp_path, scale=6, border=2)
        with open(tmp_path, encoding="utf-8") as f:
            svg = f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    # quitar la declaracion XML para embeber limpio en HTML
    svg = svg[svg.find("<svg"):]

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Abrir desde celular</title>
  <script src="/static/tailwind.cdn.js"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            walmart: {{ DEFAULT: '#00ad30', dark: '#007a22' }},
            spark:   {{ DEFAULT: '#ffc220', dark: '#995213' }},
          }}
        }}
      }}
    }}
  </script>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center p-6">
  <div class="bg-white rounded-3xl shadow-lg border border-gray-100 p-8 max-w-sm w-full text-center">

    <span class="text-spark font-black text-4xl">*</span>
    <h1 class="text-lg font-black text-gray-800 mt-2">Productividad Ventas</h1>
    <p class="text-sm text-gray-500 mt-1 mb-6">
      Escanea el QR con tu celular o escribe la liga
    </p>

    <!-- QR SVG embebido -->
    <div class="flex justify-center mb-6">
      <div class="p-3 bg-white rounded-2xl border-2 border-gray-200 inline-block">
        {svg}
      </div>
    </div>

    <!-- URL copiable -->
    <div class="bg-gray-100 rounded-xl px-4 py-3 mb-4">
      <p class="text-xs text-gray-400 mb-1">Direccion de acceso</p>
      <p class="font-mono font-bold text-walmart text-base select-all">{url}</p>
    </div>

    <p class="text-[11px] text-gray-400">
      Tu celular debe estar en la misma red WiFi (Eagle).<br>
      Puerto: <span class="font-semibold">{port}</span>
    </p>

    <button
      onclick="navigator.clipboard.writeText('{url}').then(() => this.textContent='Copiado!').catch(()=>{{}})"
      class="mt-4 w-full bg-walmart hover:bg-walmart-dark text-white font-bold
             py-2.5 rounded-xl text-sm transition">
      Copiar liga
    </button>
  </div>
</body>
</html>"""
    return HTMLResponse(content=html)
