# === utils/helpers.py ===
def generate_sku(product):
    name_prefix = product.name[:3].upper() if product.name else 'XXX'
    gender_prefix = product.gender[0].upper() if product.gender else 'X'
    size_prefix = product.size.replace('-', '').upper() if product.size else 'XX'
    color_prefix = product.color_print[:3].upper() if product.color_print else 'XXX'

    from models.product import Product
    count = Product.query.filter(
        Product.name.like(f"{product.name[:3]}%"),
        Product.gender == product.gender,
        Product.size == product.size,
        Product.color_print.like(f"{product.color_print[:3]}%")
    ).count()

    return f"{name_prefix}-{gender_prefix}-{size_prefix}-{color_prefix}-{count+1:03d}"