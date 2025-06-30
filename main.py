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

# Encabezados
sheet.clear()
sheet.append_row([
    "Nro Compra", "Fecha", "Cliente", "DNI", "Email", "Medio de Pago", "SKU",
    "Producto", "Precio Producto", "Descuento", "Envío", "Total"
])

# Carga de datos
for order in orders:
    order_id = order["id"]
    fecha = order.get("created_at", "")
    cliente = order.get("customer", {}).get("name", "")
    dni = order.get("customer", {}).get("identification", "")
    email = order.get("contact_email", "")
    pago = order.get("gateway", "")
    descuento = order.get("discount_amount", "")
    envio = order.get("shipping_cost", "")
    total = order.get("total", "")

    for product in order["products"]:
        sku = product.get("sku", "")
        nombre_producto = product.get("name", "")
        precio = product.get("price", "")

        sheet.append_row([
            order_id, fecha, cliente, dni, email, pago, sku,
            nombre_producto, precio, descuento, envio, total
        ])
