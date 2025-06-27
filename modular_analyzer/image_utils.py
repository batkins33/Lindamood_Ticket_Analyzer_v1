# --- modular_analyzer/image_utils.py ---

import os


def save_crop_and_thumbnail(img, crops_dir, filename, thumbnails_dir, thumbnail_log):
    crop_path = os.path.join(crops_dir, f"{filename}.jpg")
    img.save(crop_path)

    thumb = img.copy()
    thumb.thumbnail((150, 150))
    thumb_path = os.path.join(thumbnails_dir, f"thumb_{filename}.jpg")
    thumb.save(thumb_path)

    page_num = int(filename.split('_')[-1])
    field_name = '_'.join(filename.split('_')[:-1])
    thumbnail_log.append({"Page": page_num, "Field": field_name, "ThumbnailPath": thumb_path})


def save_field(img, save_dir, filename):
    path = os.path.join(save_dir, f"{filename}.jpg")
    img.save(path)


def sanitize_box(box, img_width, img_height):
    x1, y1, x2, y2 = box
    x1 = max(0, min(img_width, x1))
    x2 = max(0, min(img_width, x2))
    y1 = max(0, min(img_height, y1))
    y2 = max(0, min(img_height, y2))

    if x2 - x1 < 1 or y2 - y1 < 1:
        return None

    return x1, y1, x2, y2


def inches_to_pixels(position_inches, size_inches, dpi=72):
    x, y = position_inches
    w, h = size_inches
    return int(x * dpi), int(y * dpi), int((x + w) * dpi), int((y + h) * dpi)
