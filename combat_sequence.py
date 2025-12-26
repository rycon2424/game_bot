import time
import click_exclamation

class CombatSequence:
    """
    Handles the combat loop:
    - Checks for 'attack_button.png' and clicks it
    - Checks for 'exit_combat.png' and clicks it to end the loop
    """
    def __init__(self, attack_image="attack_button.png", exit_image="exit_combat.png", check_interval=1.0):
        self.attack_image = attack_image
        self.exit_image = exit_image
        self.check_interval = check_interval
        self.running = False

    def start_combat(self):
        print("Starting combat sequence...")
        self.running = True

        while self.running:
            # Check for exit first
            exit_clicked = click_exclamation.click_template(self.exit_image, max_attempts=1)
            if exit_clicked:
                print("Exit combat button found and clicked. Ending combat loop.")
                self.running = False
                break

            # Check for attack button
            attack_clicked = click_exclamation.click_template(self.attack_image, max_attempts=1)
            if attack_clicked:
                print("Attack button clicked. Waiting before next check...")

            # Wait before checking again
            time.sleep(self.check_interval)
