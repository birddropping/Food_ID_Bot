import base64
import io

from PIL import Image


def encode_image_for_api(uploaded_file) -> tuple[str, str]:
    """
    Encode a Streamlit UploadedFile to base64 for the Claude API.
    Returns (base64_data, media_type).
    Resizes to ≤1568px on longest edge and converts to JPEG.
    """
    uploaded_file.seek(0)
    image = Image.open(uploaded_file)

    # Flatten alpha channel (RGBA/P) to RGB
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    elif image.mode != "RGB":
        image = image.convert("RGB")

    # Resize if largest dimension exceeds Claude's recommended max
    max_dim = 1568
    if max(image.size) > max_dim:
        ratio = max_dim / max(image.size)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)

    encoded = base64.standard_b64encode(buffer.read()).decode("utf-8")
    return encoded, "image/jpeg"
