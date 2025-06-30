from flask import Flask, request
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime

app = Flask(__name__)

# === VARIABLES DE APP ===
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://tiendanube-exportador.onrender.com/callback"

# === FUNCIÓN PARA EXPORTAR ORDENES A SHEET ===
def exportar_ordenes(store_id, access_token):
    # Google Sheets
    google_credentials_json = os.getenv("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(google_credentials_json)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("reporte-ventas-Fibransur_2025").sheet1

    # API Tiendanube
    url = f"https://api.tiendanube.com/v1/{store_id}/orders?per_page=200&sort_by=number&sort_order=asc"
    headers = {
        "Authentication": f"bearer {access_token}",
        "Content-Type": "application/json"
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Error {res.status_code}: {res.text}")

    orders = res.json()
    orders = sorted(orders, key=lambda o: o.get("number", 0))

    # Limpiar y escribir
    sheet.clear()
    sheet.append_row([
        "Orden", "Fecha", "Cliente", "DNI", "Medio de pago",
        "SKU", "Producto", "Precio de producto", "Cantidad",
        "Descuento", "Envío", "Total"
    ])

    for order in orders:
        try:
            fecha = datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m")
        except:
            fecha = ""

        nro_orden = order.get("number", "")
        cliente = order.get("contact_name", "")
        dni = order.get("contact_identification", "")
        medio_pago = order.get("gateway_name") or order.get("gateway", "")
        descuento = f"$ {order.get('promotional_discount', {}).get('total_discount_amount', '0.00')}"
        envio = f"$ {order.get('shipping_cost_owner', '0.00')}"
        total = f"$ {order.get('total', '0.00')}"

        for product in order.get("products", []):
            nombre = product.get("name", "")
            sku = product.get("sku", "")
            precio = f"$ {product.get('price', '0.00')}"
            cantidad = product.get("quantity", 1)

            sheet.append_row([
                nro_orden, fecha, cliente, dni, medio_pago,
                sku, nombre, precio, cantidad,
                descuento, envio, total
            ])

# === HOME SIMPLE PARA CHEQUEO ===
@app.route("/")
def home():
    return "App Exportador de Tiendanube funcionando."

# === CALLBACK DE TIENDANUBE PARA GUARDAR TOKEN Y EXPORTAR ===
@app.route("/callback")
def callback():
    code = request.args.get("code")
    store_id = request.args.get("store_id")

    if not code or not store_id:
        return "Faltan parámetros 'code' o 'store_id'.", 400

    token_url = "https://www.tiendanube.com/apps/authorize/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, json=payload)
    if response.status_code != 200:
        return f"Error al obtener access_token: {response.text}", 500

    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        return "No se recibió access_token", 500

    # Guardar el token (opcional, si querés usar después)
    with open(f"store_{store_id}.json", "w") as f:
        json.dump({
            "store_id": store_id,
            "access_token": access_token
        }, f)

    # Ejecutar exportación
    try:
        exportar_ordenes(store_id, access_token)
    except Exception as e:
        return f"Token obtenido, pero error al exportar: {e}", 500

    return f"Tienda {store_id} conectada y órdenes exportadas a Google Sheets."

# === EJECUTAR FLASK SI CORRÉS LOCAL ===
if __name__ == "__main__":
    app.run()
