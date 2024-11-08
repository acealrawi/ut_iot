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
        self.action_values = {key: idx for idx, key in enumerate(actions, start=1)}
        self.formatter = {idx: key for idx, key in enumerate(actions, start=1)}
        self.current_action = None
        self.previous_action = None
        self.verbosity = config.Config().get_or("verbosity", 0)
        self.state = state
        self.action_to_execute = None

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

        opposite_actions = {
            "back1": "front1",
            "front1": "back1",
            "left1": "right1",
            "right1": "left1"
        }

        if self.current_action != "still1" and self.current_action == self.previous_action:
            self.action_to_execute = self.previous_action
        elif self.current_action == "still1" and self.previous_action:
            self.action_to_execute = self.previous_action
        elif (self.current_action in opposite_actions and
            self.previous_action == opposite_actions[self.current_action]):
            self.action_to_execute = "still1"
            self.previous_action = "still1"
        else:
            self.action_to_execute = self.current_action
            self.previous_action = self.current_action

        self.actions[self.action_to_execute](self.state)
        self.current_action = None

def mouse(address):
    off_diagonal = 10
    diagonal = math.sqrt(math.pow(off_diagonal, 2) + math.pow(off_diagonal, 2))

    return Controller("mouse", address, {
        "still1": lambda state: None,
        "back1": lambda state: pyautogui.moveRel(0, off_diagonal),
        "front1": lambda state: pyautogui.moveRel(0, -off_diagonal),
        "left1": lambda state: pyautogui.moveRel(-off_diagonal, 0),
        "right1": lambda state: pyautogui.moveRel(off_diagonal, 0)
    }, {"c": "still1", "l": "still1", "x": 0, "y": 0})

def movement(address):
    def key_press(state, keys):
        for button in state["pressed"]:
            pyautogui.keyUp(button)

        for button in keys:
            pyautogui.keyDown(button)

        state["pressed"] = keys

    return Controller("keyboard", address, {
        "still1": lambda state: key_press(state, []),
        "back1": lambda state: key_press(state, ['s']),
        "front1": lambda state: key_press(state, ['w']),
        "left1": lambda state: key_press(state, ['a']),
        "right1": lambda state: key_press(state, ['d']),
    }, {"pressed": []})
