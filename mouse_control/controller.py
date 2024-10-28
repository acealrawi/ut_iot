import config
import asyncio
import bleak
import pyautogui
import math
import time

class Controller:

    def __init__(self, name, address, actions, state):
        self.name = name
        self.address = address
        self.actions = actions
        self.current_action = None
        self.verbosity = config.Config().get_or("verbosity", 0)
        self.state = state

    def _parse_data(self, data):
        result = ""

        for service_id, service_data in data.service_data.items():
            parts = service_data.split(b'\x00\x00')[-1]
            extracted_value = parts.split(b';')[0]
            result = extracted_value.decode('utf-8')

            if self.verbosity > 1:
                print(f"{self.name} :: {self.address} :: advertisement_callback :: _parse_data :: extracted {result}")

        if result == "":
            raise RuntimeError("failed to extract any data!")

        return result

    def advertisement_callback(self, device, advertisement_data):
        if device.address.lower() == self.address.lower():
            try:
                if self.verbosity > 1:
                    print(f"{self.name} :: {self.address} :: advertisement_callback :: {advertisement_data}")
                self.current_action = self._parse_data(advertisement_data)
            except Exception as e:
                if self.verbosity > 0:
                    print(f"{self.name} :: {self.address} :: advertisement_callback :: {e}")

    def __call__(self):

        if self.current_action is None:
            return

        if self.verbosity > 0:
            print(f"{self.name} :: {self.address} :: executing action for {self.current_action}")

        self.actions[self.current_action](self.state)
        self.current_action = None


def mouse(address):
    off_diagonal = 10
    diagonal = math.sqrt(math.pow(off_diagonal, 2) + math.pow(off_diagonal, 2))
    return Controller("mouse", address, {
        "still": lambda state: None,
        "back": lambda state: pyautogui.moveRel(0, off_diagonal, duration=1),
        "front": lambda state: pyautogui.moveRel(0, -off_diagonal, duration=1),
        "left": lambda state: pyautogui.moveRel(-off_diagonal, 0, duration=1),
        "right": lambda state: pyautogui.moveRel(off_diagonal, 0, duration=1)
    }, {})

def keyboard(address):
    def key_press(state, keys):
        for button in state["pressed"]:
            pyautogui.keyUp(button)

        for button in keys:
            pyautogui.keyDown(button)

        state["pressed"] = keys

    return Controller("keyboard", address, {
        "still": lambda state: key_press(state, []),
        "back": lambda state: key_press(state, ['s']),
        "front": lambda state: key_press(state, ['w']),
        "left": lambda state: key_press(state, ['a']),
        "right": lambda state: key_press(state, ['d']),
    }, {"pressed": []})
