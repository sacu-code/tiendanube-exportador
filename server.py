from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "¡Hola! Esta es la app de exportación de Tiendanube."

@app.route("/callback")
def callback():
    code = request.args.get("code")
    return f"Autorización recibida. Código: {code}"

@app.route("/webhooks/store-redact", methods=["POST"])
def store_redact():
    return "OK", 200

@app.route("/webhooks/customers-redact", methods=["POST"])
def customers_redact():
    return "OK", 200

@app.route("/webhooks/customers-data-request", methods=["POST"])
def customers_data_request():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
