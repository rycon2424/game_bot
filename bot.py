import mss
import numpy as np
import pytesseract
import cv2
import re
import click_exclamation
import time
from combat_sequence import CombatSequence
from enemy_clicker import EnemyClicker

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
        current = int(digits[0])
        maximum = int(digits[1])
        return current, maximum
    else:
        return None, None

def wait_for_start_combat(max_attempts=5):
    """Try to find start_combat.png with fallback logic."""
    attempts = 0
    while attempts < max_attempts:
        found = click_exclamation.click_template("start_combat.png", max_attempts=1, wait_between=0.3)
        if found:
            return True
        attempts += 1
    print("Failed to find start_combat.png after multiple attempts, retrying main loop...")
    return False

def ensure_exit_combat():
    """Ensure exit_combat.png is clicked after combat ends."""
    while True:
        clicked = click_exclamation.click_template("exit_combat.png", max_attempts=1)
        if not clicked:
            print("exit_combat.png not found anymore, combat fully exited.")
            break
        print("exit_combat.png still visible, retrying in 0.5s...")
        time.sleep(0.5)

def perform_actions():
    current, maximum = read_health()
    if current is None:
        print("OCR unreliable, skipping this cycle.")
        return

    print(f"Health: {current}/{maximum}")

    if current == maximum:
        # Step 1: try clicking exclamation marks
        clicked = click_exclamation.click_template("exclamation.png")
        if clicked:
            print("Exclamation clicked, waiting for start_combat.png...")
        else:
            # Step 2: no exclamation, check for moving enemies
            print("No exclamation found, checking for moving enemies...")
            enemy_clicker = EnemyClicker()
            enemy_clicked = enemy_clicker.detect_and_click(max_attempts=10)
            if not enemy_clicked:
                print("No movement detected, nothing to do.")
                return
            print("Enemy clicked, waiting for start_combat.png...")

        # Step 3: wait for start_combat.png with fallback
        start_clicked = wait_for_start_combat(max_attempts=5)
        if not start_clicked:
            return  # fallback: retry main loop

        # Step 4: start the combat loop
        combat = CombatSequence()
        combat.start_combat()

        # Step 5: ensure exit button is clicked if missed
        ensure_exit_combat()

        print("Combat finished, returning to main loop.")
    else:
        print("Health not full, skipping actions.")

if __name__ == "__main__":
    print("Bot started. Press Ctrl+C to stop.")
    try:
        while True:
            perform_actions()
            time.sleep(2)  # small delay to reduce CPU usage
    except KeyboardInterrupt:
        print("Bot stopped by user.")
