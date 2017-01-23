from PIL import Image
from resizeimage import resizeimage

THUMBNAIL_SIZE = (265, 265)


def resize_project_thumbnail(fullpath, size=THUMBNAIL_SIZE):
    # If a single int is given, assume a square of that size
    if type(size) == int:
        size = (size, size)

    # Resize and replace the given image
    with open(fullpath, 'r+b') as original_image:
        with Image.open(original_image) as img:
            thumbnail = resizeimage.resize_thumbnail(img, size)
            thumbnail.save(fullpath, img.format)
