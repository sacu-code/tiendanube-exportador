from datetime import datetime

sheet.clear()
sheet.append_row(["Nro Orden", "Email", "Fecha", "Cliente", "DNI", "Medio de pago", "SKU", "Producto", "Precio producto", "Descuento", "Costo envío", "Total"])

for order in orders:
    fecha = datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m")
    nro_compra = order.get("number", "")
    email = order.get("contact_email", "")
    cliente = order.get("contact_name", "")
    dni = order.get("contact_identification", "")
    medio_pago = order.get("gateway_name", "")
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
