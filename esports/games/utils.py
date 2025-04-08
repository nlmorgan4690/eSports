import os
import secrets
from PIL import Image
from flask import current_app
from PIL import Image, UnidentifiedImageError

def save_game_icon(form_icon):
    if not form_icon or form_icon.filename == '':
        return None  # No new image uploaded

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_icon.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/game_icons', picture_fn)

    try:
        output_size = (256, 256)
        i = Image.open(form_icon)
        i.thumbnail(output_size)
        i.save(picture_path)
        return picture_fn
    except UnidentifiedImageError:
        raise ValueError("The uploaded file is not a valid image.")
