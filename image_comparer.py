import cv2
import numpy as np
import pyautogui
import mss
import time
import os

IMAGES_FOLDER = "images"

def click_template(image_name, threshold=0.85, max_attempts=1, wait_between=0.2):
    template_path = os.path.join(IMAGES_FOLDER, image_name)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    if template is None:
        print(f"Template not found: {template_path}")
        return False

    t_h, t_w = template.shape[:2]
    attempts = 0

    while attempts < max_attempts or max_attempts == -1:
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])
            screen = np.array(screenshot)

        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        if len(locations[0]) > 0:
            y = int(locations[0][0] + t_h / 2)
            x = int(locations[1][0] + t_w / 2)
            pyautogui.click(x, y)
            return True

        attempts += 1
        time.sleep(wait_between)

    return False


# FRAME-BASED HELPERS
def capture_frame():
    """Capture a single full-screen frame."""
    with mss.mss() as sct:
        return np.array(sct.grab(sct.monitors[1]))


def find_template_on_frame(frame, image_name, threshold=0.85):
    """
    Detects a template on a PROVIDED frame.
    Returns (x, y) or None.
    """
    template_path = os.path.join(IMAGES_FOLDER, image_name)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    if template is None:
        return None

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape
        x = max_loc[0] + w // 2
        y = max_loc[1] + h // 2
        return x, y

    return None

def find_powerup_ready_on_frame(frame, image_name, threshold=0.8, detail_threshold=15):
    """
    Detects a ready powerup by:
    - matching the yellow circle
    - rejecting matches with flat (empty) inner areas
    """
    template_path = os.path.join(IMAGES_FOLDER, image_name)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        return None

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        return None

    h, w = template.shape
    cx = max_loc[0] + w // 2
    cy = max_loc[1] + h // 2

    # --- INNER DETAIL CHECK ---
    inner_radius = int(min(w, h) * 0.25)
    inner = frame_gray[
        cy - inner_radius : cy + inner_radius,
        cx - inner_radius : cx + inner_radius
    ]

    if inner.size == 0:
        return None

    variance = np.var(inner)

    # Empty slot = very low variance
    if variance < detail_threshold:
        return None

    return cx, cy
