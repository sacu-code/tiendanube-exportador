import os
import json
import requests
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# === CREDENCIALES DESDE VARIABLES DE ENTORNO ===
ACCESS_TOKEN = os.getenv("TIENDANUBE_TOKEN")
STORE_ID = os.getenv("TIENDANUBE_USER_ID")

# Configurar credenciales de Google Sheets desde variable
google_credentials_json = os.getenv("GOOGLE_CREDENTIALS")
creds_dict = json.loads(google_credentials_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Acceder a la hoja
sheet = client.open("reporte-ventas-Fibransur_2025").sheet1
sheet.clear()

# Cabecera
sheet.append_row([
    "Nro Compra", "Email", "Fecha", "Cliente", "DNI", "Medio de pago",
    "SKU", "Producto", "Precio producto", "Descuento", "Costo envío", "Total"
])

# === LLAMADA A API DE TIENDANUBE ===
url = f"https://api.tiendanube.com/v1/{STORE_ID}/orders?per_page=200"
headers = {
    "Authentication": f"bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

res = requests.get(url, headers=headers)
if res.status_code != 200:
    raise Exception(f"Error {res.status_code}: {res.text}")

orders = res.json()

# === PROCESAR Y EXPORTAR PEDIDOS ===
for order in orders:
    try:
        fecha = datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m")
    except:
        fecha = order["created_at"][:10]  # fallback
    
    nro_compra = order.get("number", "")
    email = order.get("contact_email", "")
    cliente = order.get("contact_name", "")
    dni = order.get("contact_identification", "")
    medio_pago = order.get("payment_details", {}).get("method", "")
    descuento = order.get("promotional_discount", {}).get("total_discount_amount", "")
    envio = order.get("shipping_cost_owner", "")
    total = order.get("total", "")

    for product in order["products"]:
        nombre = product.get("name", "")
        sku = product.get("sku", "")
        precio = product.get("price", "")

        sheet.append_row([
            nro_compra, email, fecha, cliente, dni, medio_pago,
            sku, nombre, precio, descuento, envio, total
        ])
