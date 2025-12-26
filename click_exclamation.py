import cv2
import numpy as np
import pyautogui
import mss
import time
import os

IMAGES_FOLDER = "images"

def click_template(image_name, threshold=0.85, max_attempts=1, wait_between=0.2):
    """
    Searches for the template image on screen and clicks it.
    
    - image_name: filename inside images folder
    - threshold: matching threshold (0-1)
    - max_attempts: number of times to search (if >1, repeats)
    - wait_between: seconds to wait between attempts
    """
    template_path = os.path.join(IMAGES_FOLDER, image_name)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"Template not found: {template_path}")
        return False

    t_h, t_w = template.shape[:2]

    found = False
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

            print(f"Found {image_name} at {x},{y}, clicking...")
            pyautogui.click(x, y)
            found = True
            break

        attempts += 1
        time.sleep(wait_between)

    if not found:
        print(f"{image_name} not found")
    return found