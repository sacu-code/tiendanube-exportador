import requests
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# CONFIG
ACCESS_TOKEN = os.getenv("TIENDANUBE_TOKEN")
STORE_ID = os.getenv("TIENDANUBE_USER_ID")

# Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("reporte-ventas-Fibransur_2025").sheet1

# API call
url = f"https://api.tiendanube.com/v1/{STORE_ID}/orders?per_page=3"
headers = {
    "Authentication": f"bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

res = requests.get(url, headers=headers)
if res.status_code != 200:
    raise Exception(f"Error {res.status_code}: {res.text}")

orders = res.json()
print(f"Pedidos encontrados: {len(orders)}")

if not orders:
    print("No hay pedidos.")
else:
    for i, order in enumerate(orders):
        print(f"\n--- Pedido #{i+1} ---")
        print(json.dumps(order, indent=2, ensure_ascii=False))
