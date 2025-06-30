
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# CONFIGURACIÓN
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
STORE_ID = 6250679

# Conexión a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("VENTAS TIENDANUBE").sheet1

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
sheet.append_row(["Nro Orden", "Email", "Fecha", "Total", "Producto", "Cantidad"])

for order in orders:
    for product in order["products"]:
        sheet.append_row([
            order["id"],
            order.get("contact_email", ""),
            order.get("created_at", ""),
            order.get("total", ""),
            product.get("name", ""),
            product.get("quantity", "")
        ])
