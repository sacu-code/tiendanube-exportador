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
url = f"https://api.tiendanube.com/v1/{STORE_ID}/orders?per_page=1"
headers = {
    "Authentication": f"bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

res = requests.get(url, headers=headers)
if res.status_code != 200:
    raise Exception(f"Error {res.status_code}: {res.text}")

orders = res.json()

# Mostrar en logs (Render lo va a mostrar en Logs)
print(json.dumps(orders[0], indent=2, ensure_ascii=False))
