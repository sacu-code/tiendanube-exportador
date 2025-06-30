import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime

# CONFIGURACIÓN
ACCESS_TOKEN = os.getenv("TIENDANUBE_TOKEN")
STORE_ID = os.getenv("TIENDANUBE_USER_ID")

# Conexión a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("reporte-ventas-Fibransur_2025").sheet1

# Llamada a la API
url = f"https://api.tiendanube.com/v1/{STORE_ID}/orders?per_page=200"
headers = {
    "Authentication": f"bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

res = requests.get(url, headers=headers)
if res.status_code != 200:
    raise Exception(f"Error {res.status_code}: {res.text}")

orders = res.json()

# Encabezado
sheet.clear()
sheet.append_row([
    "Orden", "Fecha", "Cliente", "DNI", "Medio de pago",
    "SKU", "Producto", "Precio de producto", "Cantidad",
    "Descuento", "Envío", "Total"
])

# Datos
for order in orders:
    try:
        fecha = datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m")
    except:
        fecha = ""

    nro_orden = order.get("number", "")
    email = order.get("contact_email", "")
    cliente = order.get("contact_name", "")
    dni = order.get("contact_identification", "")
    medio_pago = order.get("payment_details", {}).get("method", "")
    descuento = f"$ {order.get('promotional_discount', {}).get('total_discount_amount', '0.00')}"
    envio = f"$ {order.get('shipping_cost_owner', '0.00')}"
    total = f"$ {order.get('total', '0.00')}"

    for product in order["products"]:
        nombre = product.get("name", "")
        sku = product.get("sku", "")
        precio = f"$ {product.get('price', '0.00')}"
        cantidad = product.get("quantity", 1)

        sheet.append_row([
            nro_orden, fecha, cliente, dni, medio_pago,
            sku, nombre, precio, cantidad,
            descuento, envio, total
        ])
