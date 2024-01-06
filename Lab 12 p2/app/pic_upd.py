from PIL import Image
import os
import uuid

def save_picture(form_picture, save_path):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = str(uuid.uuid4()) + f_ext
    picture_path = os.path.join(save_path, picture_fn)

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_fn