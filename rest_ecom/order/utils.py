import uuid

def generate_order_number():
    order_number = str(uuid.uuid4()).replace('-', '').upper()[:10]
    return order_number