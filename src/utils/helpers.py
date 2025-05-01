# === utils/helpers.py ===
from models.product import Produto # Use the new model name

def generate_sku(produto):
    """Generates a potentially unique SKU based on product attributes."""
    # Use Portuguese field names from the Produto model
    nome_prefix = produto.nome[:3].upper().strip() if produto.nome else 'XXX'
    sexo_prefix = produto.sexo[0].upper() if produto.sexo else 'X'
    # Remove spaces and hyphens for a cleaner SKU part
    tamanho_prefix = produto.tamanho.replace('-', '').replace(' ', '').upper()[:4] if produto.tamanho else 'XXXX'
    cor_prefix = produto.cor_estampa[:3].upper().strip() if produto.cor_estampa else 'XXX'

    # Construct the base SKU part
    base_sku = f"{nome_prefix}-{sexo_prefix}-{tamanho_prefix}-{cor_prefix}"

    # Find the highest existing suffix for this base SKU
    # Query products that start with the base SKU followed by a hyphen
    like_pattern = f"{base_sku}-%"
    existing_products = Produto.query.filter(Produto.sku.like(like_pattern)).all()

    max_suffix = 0
    for p in existing_products:
        try:
            # Extract the suffix number after the last hyphen
            suffix_str = p.sku.split('-')[-1]
            suffix_num = int(suffix_str)
            if suffix_num > max_suffix:
                max_suffix = suffix_num
        except (IndexError, ValueError):
            # Handle cases where SKU format might be unexpected
            continue

    # Increment the highest suffix found
    new_suffix = max_suffix + 1

    # Return the new SKU with a padded suffix
    return f"{base_sku}-{new_suffix:03d}"

