import base64


def image_to_base64(image: bytes, format: str) -> str:
    """Кодирование изображения в строку base64."""
    image_encoded = base64.b64encode(image).decode('utf-8')
    return f'data:image/{format};base64,{image_encoded}'
