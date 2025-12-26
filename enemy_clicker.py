import mss
import numpy as np
import cv2
import pyautogui
import time
import click_exclamation

class EnemyClicker:
    """
    Detects moving enemies in a defined battlemap region
    and clicks on the movement.
    """

    def __init__(self, region=None, threshold=30, wait_between=0.2):
        """
        - region: dict with 'left', 'top', 'width', 'height'
        - threshold: pixel difference to consider movement
        - wait_between: seconds between frames
        """
        if region is None:
            # default battlemap region
            self.region = {"left": 414, "top": 308, "width": 921, "height": 503}
        else:
            self.region = region
        self.threshold = threshold
        self.wait_between = wait_between

    def detect_and_click(self, max_attempts=10):
        """
        Looks for movement in the battlemap region and clicks on the first moving spot.
        Returns True if a click was performed.
        """
        with mss.mss() as sct:
            prev_frame = None
            attempts = 0

            while attempts < max_attempts:
                screenshot = sct.grab(self.region)
                frame = np.array(screenshot)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if prev_frame is None:
                    prev_frame = gray
                    time.sleep(self.wait_between)
                    attempts += 1
                    continue

                # Compute absolute difference between frames
                diff = cv2.absdiff(prev_frame, gray)
                _, diff_thresh = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)

                # Find contours of movement
                contours, _ = cv2.findContours(diff_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    # Click center of first moving contour
                    cnt = contours[0]
                    x, y, w, h = cv2.boundingRect(cnt)
                    click_x = self.region["left"] + x + w // 2
                    click_y = self.region["top"] + y + h // 2

                    print(f"Detected movement at {click_x},{click_y}, clicking...")
                    pyautogui.click(click_x, click_y)
                    return True

                prev_frame = gray
                time.sleep(self.wait_between)
                attempts += 1

        print("No movement detected in battlemap.")
        return False
