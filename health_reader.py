import mss
import numpy as np
import pytesseract
import cv2
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

HEALTH_REGION = {
    "left": 420,
    "top": 167,
    "width": 40,
    "height": 9
}

def read_health():
    with mss.mss() as sct:
        screenshot = sct.grab(HEALTH_REGION)
        img = np.array(screenshot)

    # Stage 1: original crop
    # Stage 2: grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Stage 3: resize
    gray_resized = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # OCR
    config = "--psm 7 -c tessedit_char_whitelist=0123456789/"
    text = pytesseract.image_to_string(gray_resized, config=config)

    # Extract digits
    digits = re.findall(r"\d+", text)
    if len(digits) >= 2:
        return int(digits[0]), int(digits[1])
    return None, None
