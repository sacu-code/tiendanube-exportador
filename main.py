import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

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

# Limpia y carga encabezados
sheet.clear()
sheet.append_row([
    "Nro Compra", "Fecha", "Cliente", "DNI", "Medio de pago",
    "SKU", "Producto", "Precio de producto", "Cantidad",
    "Descuento", "Envío", "Total"
])

# Carga datos por producto
for order in orders:
    order_id = order.get("number", order.get("id"))
    date = order.get("created_at", "")
    cliente = order.get("customer", {}).get("name", "")
    dni = order.get("customer", {}).get("identification", "")
    medio_pago = order.get("payment_details", {}).get("method", "")
    descuento = order.get("discount", "0.00")
    envio = order.get("shipping_cost_owner", "0.00")
    total = order.get("total", "0.00")

    for product in order.get("products", []):
        sku = product.get("sku", "")
        nombre = product.get("name", "")
        precio = product.get("price", "0.00")
        cantidad = product.get("quantity", 1)

        sheet.append_row([
            order_id,
            date,
            cliente,
            dni,
            medio_pago,
            sku,
            nombre,
            precio,
            cantidad,
            descuento,
            envio,
            total
        ])
