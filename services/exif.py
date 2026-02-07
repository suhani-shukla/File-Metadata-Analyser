from PIL import Image
import mimetypes
import os

def extract_exif_metadata(file_path):
    exif_metadata = {}
    sensitive_fields = []

    mime_type = mimetypes.guess_type(file_path)[0]

    if not mime_type or not mime_type.startswith("image"):
        return exif_metadata, sensitive_fields

    with Image.open(file_path) as img:
        width, height = img.size

        exif_metadata["image_width"] = width
        exif_metadata["image_height"] = height
        exif_metadata["image_size"] = f"{width}x{height}"
        exif_metadata["megapixels"] = round((width * height) / 1_000_000, 3)

        exif_metadata["color_type"] = img.mode
        exif_metadata["bit_depth"] = img.bits if hasattr(img, "bits") else "Unknown"
        exif_metadata["compression"] = img.info.get("compression", "Unknown")
        exif_metadata["gamma"] = img.info.get("gamma", "Unknown")
        exif_metadata["srgb_rendering"] = img.info.get("srgb", "Unknown")

        dpi = img.info.get("dpi")
        if dpi:
            exif_metadata["pixels_per_unit_x"] = dpi[0]
            exif_metadata["pixels_per_unit_y"] = dpi[1]
            exif_metadata["pixel_units"] = "inches"

        exif_metadata["file_format"] = img.format
        exif_metadata["category"] = "image"

        # Raw header (first 64 bytes)
        with open(file_path, "rb") as f:
            raw_bytes = f.read(64)
            # Convert to spaced hex format
            formatted_header = " ".join(f"{b:02X}" for b in raw_bytes)
            exif_metadata["raw_header"] = formatted_header

        # Sensitive detection
        for key in exif_metadata:
            if any(x in key.lower() for x in ["gps", "device", "camera", "model"]):
                sensitive_fields.append(key)

    return exif_metadata, sensitive_fields
