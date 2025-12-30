import mss
import numpy as np
import pytesseract
import cv2
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

HEALTH_REGION = {
    "left": 425,
    "top": 167,
    "width": 36,
    "height": 9
}

HP_BAR_LEFT_HALF = {
    "left": 385,
    "top": 167,
    "width": 40,
    "height": 8
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
    cv2.imwrite("debug_stage3_resized.png", gray_resized)

    # OCR
    config = "--psm 7 -c tessedit_char_whitelist=0123456789/"
    text = pytesseract.image_to_string(gray_resized, config=config)

    # Extract digits
    digits = re.findall(r"\d+", text)
    if len(digits) >= 2:
        return int(digits[0]), int(digits[1])
    return None, None

def is_hp_bar_low(threshold_ratio=0.5):
    return read_hp_bar_red_ratio() > threshold_ratio

def read_hp_bar_red_ratio():
    with mss.mss() as sct:
        img = np.array(sct.grab(HP_BAR_LEFT_HALF))

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 40])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 120, 40])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 | mask2

    red_pixels = np.count_nonzero(red_mask)
    total_pixels = red_mask.size

    return red_pixels / total_pixels

def capture_hp_bar_debug(filename="debug_hp_bar.png"):
    with mss.mss() as sct:
        img = np.array(sct.grab(HP_BAR_LEFT_HALF))
    cv2.imwrite(filename, img)