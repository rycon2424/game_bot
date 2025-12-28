import mss
import numpy as np
import pytesseract
import cv2
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

HEALTH_REGION = {
    "left": 425,
    "top": 162,
    "width": 50,
    "height": 20
}

def read_health():
    with mss.mss() as sct:
        screenshot = sct.grab(HEALTH_REGION)
        img = np.array(screenshot)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

    config = "--psm 7 -c tessedit_char_whitelist=0123456789/"
    text = pytesseract.image_to_string(thresh, config=config)

    digits = re.findall(r"\d+", text)

    if len(digits) >= 2:
        return int(digits[0]), int(digits[1])
    return None, None
