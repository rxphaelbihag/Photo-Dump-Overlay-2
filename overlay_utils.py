# overlay_utils.py
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()  # Enables HEIF/HEIC support globally


def apply_overlay(base_image_path: str,
                  overlay_landscape_path: str,
                  overlay_portrait_path: str,
                  output_path: str) -> None:
    """
    Composites a transparent overlay onto a base image and saves the result.

    - Picks the landscape or portrait overlay based on the base image's orientation.
    - Scales the overlay to fully cover the base (aspect preserved, excess cropped).
    - Pastes the overlay centered using its alpha channel as the mask.
    """
    base = Image.open(base_image_path).convert("RGBA")
    base = ImageOps.exif_transpose(base)

    bw, bh = base.size
    overlay_path = overlay_landscape_path if bw >= bh else overlay_portrait_path
    overlay = Image.open(overlay_path).convert("RGBA")

    # Scale + center-crop overlay to match base dimensions exactly
    overlay = ImageOps.fit(
        overlay, base.size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )

    base.paste(overlay, (0, 0), overlay)
    base.convert("RGB").save(output_path, quality=95)