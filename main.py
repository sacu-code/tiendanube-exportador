import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime

# CONFIGURACIÓN
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
STORE_ID = 6250679

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

# Limpia y carga la hoja
sheet.clear()
sheet.append_row(["Nro Orden", "Email", "Fecha", "Cliente", "DNI", "Medio de pago", "SKU", "Producto", "Precio producto", "Descuento", "Costo envío", "Total"])

for order in orders:
    fecha = datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m")
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
