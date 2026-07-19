"""Sube auth.py corregido a GitHub para triggear redeploy en Render."""
import base64, json, urllib.request, urllib.error, sys

USUARIO = "jahandyhdz-code"
REPO    = "tablero-productividad"

token = input("Pega tu token de GitHub (ghp_...): ").strip()

def github(url, method="GET", data=None):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "fix-deploy",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

files_to_push = [
    "database.py",
    "templates/base.html",
    "templates/admin.html",
    "routers/auth_router.py",
    "routers/admin_router.py",
    "auth.py",
]

for fname in files_to_push:
    print(f"\nSubiendo {fname}...")
    content = open(fname, "rb").read()

    # Obtener SHA actual
    resp, status = github(f"https://api.github.com/repos/{USUARIO}/{REPO}/contents/{fname}")
    sha = resp.get("sha") if status == 200 else None

    data = {
        "message": f"fix: compatibilidad PostgreSQL en {fname}",
        "content": base64.b64encode(content).decode(),
    }
    if sha:
        data["sha"] = sha

    _, status = github(
        f"https://api.github.com/repos/{USUARIO}/{REPO}/contents/{fname}",
        "PUT", data
    )
    print(f"  {'OK' if status in (200,201) else 'ERROR: ' + str(status)}")

print("\nListo! Render va a hacer redeploy automatico en ~2 minutos.")
print("Checa el dashboard de Render en tu celular.")
