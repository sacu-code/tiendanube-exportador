import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime

# CONFIGURACIÓN desde Environment Variables
ACCESS_TOKEN = os.getenv("TIENDANUBE_TOKEN")
STORE_ID = os.getenv("TIENDANUBE_USER_ID")

# Google Sheets credentials desde variable secreta
google_credentials_json = os.getenv("GOOGLE_CREDENTIALS")
creds_dict = json.loads(google_credentials_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("reporte-ventas-Fibransur_2025").sheet1

# Llamada a la API de Tiendanube
url = f"https://api.tiendanube.com/v1/{STORE_ID}/orders?per_page=200"
headers = {
    "Authentication": f"bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
res = requests.get(url, headers=headers)
if res.status_code != 200:
    raise Exception(f"Error {res.status_code}: {res.text}")
orders = res.json()

# Limpiar y escribir encabezado
sheet.clear()
sheet.append_row([
    "Orden", "Fecha", "Cliente", "DNI", "Medio de pago",
    "SKU", "Producto", "Precio de producto", "Cantidad",
    "Descuento", "Envío", "Total"
])

# Cargar datos
for order in orders:
    fecha_cruda = order.get("created_at", "")
    try:
        fecha_formateada = datetime.strptime(fecha_cruda[:10], "%Y-%m-%d").strftime("%d/%m")
    except:
        fecha_formateada = ""

    nro_compra = order.get("number", "")
    email = order.get("contact_email", "")
    cliente = order.get("contact_name", "")
    dni = order.get("contact_identification", "")
    medio_pago = order.get("payment_details", {}).get("method", "")
    descuento = order.get("promotional_discount", {}).get("total_discount_amount", "0.00")
    envio = order.get("shipping_cost_owner", "")
    total = order.get("total", "")

    for product in order["products"]:
        nombre = product.get("name", "")
        sku = product.get("sku", "")
        precio = product.get("price", "")
        cantidad = product.get("quantity", "")

        sheet.append_row([
            nro_compra, fecha_formateada, cliente, dni, medio_pago,
            sku, nombre, precio, cantidad, descuento, envio, total
        ])
