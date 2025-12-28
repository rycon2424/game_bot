import time
import pyautogui
from health_reader import read_health
from image_comparer import (
    click_template,
    capture_frame,
    find_template_on_frame,
    find_powerup_ready_on_frame
)


class CombatSequence:
    def __init__(
        self,
        exit_image="exit_combat.png",
        heal_image="healing_pot.PNG",
        powerup_image="powerup_available.PNG",
        attack_default="attack_default.png",
        attack_images=None,
        heal_threshold=30,
        check_interval=0.5
    ):
        self.exit_image = exit_image
        self.heal_image = heal_image
        self.powerup_image = powerup_image
        self.attack_default = attack_default
        self.attack_images = attack_images or [
            "attack_left.PNG",
            "attack_right.PNG",
            "attack_up.PNG",
        ]
        self.heal_threshold = heal_threshold
        self.check_interval = check_interval
        self.running = False

    def reset_mouse_to_center(self):
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width // 2, screen_height // 2, duration=0.05)
    
    def start_combat(self):
        print("Starting combat sequence...")
        self.running = True

        while self.running:
            # 1️ Exit combat (fast path, own capture)
            if click_template(self.exit_image, max_attempts=1):
                print("Exited combat.")
                break

            # 2️ Health check → heal
            current, _ = read_health()
            print(f"Current read health value = {current}")
            #if current is not None and current < self.heal_threshold:
            #    if click_template(self.heal_image, max_attempts=1):
            #        print(f"Low HP ({current}), used healing.")
            #        time.sleep(self.check_interval)
            #        continue

            # 3️ Capture ONE frame for all attacks
            frame = capture_frame()

            # 4️ Power-up (highest priority)
            pos = find_powerup_ready_on_frame(frame, self.powerup_image)
            if pos:
                pyautogui.click(*pos)
                print("Power-up activated.")
                time.sleep(self.check_interval)
                continue

            # 5️ Directional attacks (same frame)
            for attack_image in self.attack_images:
                pos = find_template_on_frame(frame, attack_image)
                if pos:
                    pyautogui.click(*pos)
                    print(f"Directional attack: {attack_image}")
                    time.sleep(self.check_interval)
                    break
            else:
            # 6️ Default attack fallback (same frame)
                pos = find_template_on_frame(frame, self.attack_default)
                if pos:
                    pyautogui.click(*pos)
                    print("Default attack.")

            time.sleep(self.check_interval)
            self.reset_mouse_to_center()
            time.sleep(self.check_interval)