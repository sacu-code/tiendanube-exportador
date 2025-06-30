from flask import Flask, request, redirect
import requests
import json

app = Flask(__name__)

CLIENT_ID = "19066"
CLIENT_SECRET = "d0ce627cdede364eb19cb4ba64410c51db41c24661a3efb9"
REDIRECT_URI = "https://tiendanube-exportador.onrender.com/callback"

@app.route("/")
def home():
    auth_url = (
        f"https://www.tiendanube.com/apps/authorize"
        f"?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&response_type=code&scope=read_orders"
    )
    return f'<a href="{auth_url}">Conectar Tiendanube</a>'

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Falta el código de autorización"

    token_url = "https://www.tiendanube.com/apps/token"
    response = requests.post(token_url, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    })

    if response.status_code != 200:
        return f"Error obteniendo token: {response.text}"

    data = response.json()
    access_token = data["access_token"]
    user_id = data["user_id"]

    with open("auth_data.json", "w") as f:
        json.dump(data, f)

    return f"✅ Autenticado con éxito<br><br>Access Token: {access_token}<br>Store ID: {user_id}<br><br><a href='/ventas'>Ver ventas</a>"

@app.route("/ventas")
def ventas():
    try:
        with open("auth_data.json", "r") as f:
            auth = json.load(f)
    except:
        return "⚠️ Primero conectá una tienda desde /"

    token = auth["access_token"]
    store_id = auth["user_id"]

    headers = {
        "Authentication": f"bearer {token}",
        "User-Agent": f"{store_id} - Exportador Ventas"
    }

    r = requests.get(f"https://api.tiendanube.com/v1/{store_id}/orders", headers=headers)

    if r.status_code != 200:
        return f"Error al obtener ventas: {r.text}"

    ventas = r.json()
    return json.dumps(ventas, indent=2)

if __name__ == "__main__":
    app.run(port=8080)
