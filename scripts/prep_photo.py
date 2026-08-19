#!/usr/bin/env python3
"""
prep_photo.py — one-time photo prep for the ASCII portrait pipeline.

1. Remove the background with rembg so the subject is isolated.
2. Boost local contrast with OpenCV's CLAHE.
3. Composite onto pure white so the background maps to the blank end
   of the ASCII ramp (white -> spaces).

Usage: python scripts/prep_photo.py source-photo.jpg
Output: source-prepped.png (grayscale)
"""
import sys
import os
import numpy as np
import cv2
from PIL import Image
from rembg import remove, new_session

# u2net is a much smaller/faster model than rembg's newer default
# (bria-rmbg-2.0, ~1GB) and is plenty for a portrait cutout on CPU.
_SESSION = new_session("u2net")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <input-photo>")
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = os.path.join(os.path.dirname(in_path) or ".", "source-prepped.png")

    print(f"[1/3] Removing background from {in_path} ...")
    with open(in_path, "rb") as f:
        input_bytes = f.read()
    result_bytes = remove(input_bytes, session=_SESSION)

    # Load as RGBA
    rgba = Image.open(__import__("io").BytesIO(result_bytes)).convert("RGBA")

    print("[2/3] Boosting local contrast with CLAHE ...")
    rgb = rgba.convert("RGB")
    arr = np.array(rgb)
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l_channel)
    lab_clahe = cv2.merge((l_clahe, a_channel, b_channel))
    rgb_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2RGB)
    contrasted = Image.fromarray(rgb_clahe).convert("RGBA")
    contrasted.putalpha(rgba.getchannel("A"))

    print("[3/3] Compositing onto pure white and converting to grayscale ...")
    white_bg = Image.new("RGBA", contrasted.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, contrasted).convert("L")

    composited.save(out_path)
    print(f"Saved {out_path} ({composited.size[0]}x{composited.size[1]})")


if __name__ == "__main__":
    main()
