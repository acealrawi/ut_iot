import config
import asyncio
import bleak
import pyautogui
import math
import time
import action

class Controller:

    def __init__(self, name, address, actions, state):
        self.name = name
        self.address = address
        self.actions = actions
        self.action_values = {key: idx for idx, key in enumerate(action.string_map, start=1)}
        self.formatter = {idx: key for idx, key in enumerate(action.string_map, start=1)}
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
                self.current_action = action.map_action(self._parse_data(advertisement_data))
            except Exception as e:
                if self.verbosity > 0:
                    print(f"{self.name} :: {self.address} :: advertisement_callback :: {e}")

    def __call__(self):

        if self.current_action is None:
            return

        if self.verbosity > 0:
            print(f"{self.name} :: {self.address} :: executing action for {self.current_action}")

        opposite_actions = {
            action.Action.BACK: action.Action.FRONT,
            action.Action.FRONT: action.Action.BACK,
            action.Action.LEFT: action.Action.RIGHT,
            action.Action.RIGHT: action.Action.LEFT,
        }

        if self.current_action != action.Action.STILL and self.current_action == self.previous_action:
            self.action_to_execute = self.previous_action
        elif self.current_action == action.Action.STILL and self.previous_action:
            self.action_to_execute = self.previous_action
        elif (self.current_action in opposite_actions and
            self.previous_action == opposite_actions[self.current_action]):
            self.action_to_execute = action.Action.STILL
            self.previous_action = action.Action.STILL
        else:
            self.action_to_execute = self.current_action
            self.previous_action = self.current_action

        self.actions[self.action_to_execute](self.state)
        self.current_action = None

def mouse(address):
    off_diagonal = 25
    diagonal = math.sqrt(math.pow(off_diagonal, 2) + math.pow(off_diagonal, 2))

    return Controller("mouse", address, {
        action.Action.STILL: lambda state: None,
        action.Action.BACK: lambda state: pyautogui.moveRel(0, off_diagonal),
        action.Action.FRONT: lambda state: pyautogui.moveRel(0, -off_diagonal),
        action.Action.LEFT: lambda state: pyautogui.moveRel(-off_diagonal, 0),
        action.Action.RIGHT: lambda state: pyautogui.moveRel(off_diagonal, 0)
    }, {})

def movement(address):
    def key_press(state, keys):
        for button in state["pressed"]:
            pyautogui.keyUp(button)

        for button in keys:
            pyautogui.keyDown(button)

        state["pressed"] = keys

    return Controller("keyboard", address, {
        action.Action.STILL: lambda state: key_press(state, []),
        action.Action.BACK: lambda state: key_press(state, ['s']),
        action.Action.FRONT: lambda state: key_press(state, ['w']),
        action.Action.LEFT: lambda state: key_press(state, ['a']),
        action.Action.RIGHT: lambda state: key_press(state, ['d']),
    }, {"pressed": []})

def actions(address):

    def key_press(state, keys, click=False):

        if click:
            pyautogui.mouseDown()
            return

        pyautogui.mouseUp()

        for button in state["pressed"]:
            pyautogui.keyUp(button)

        for button in keys:
            pyautogui.keyDown(button)

        state["pressed"] = keys

    return Controller("actions", address, {
        action.Action.STILL: lambda state: key_press(state, []),
        action.Action.BACK: lambda state: key_press(state, ['space']),
        action.Action.FRONT: lambda state: key_press(state, [], True),
        action.Action.LEFT: lambda state: key_press(state, []),
        action.Action.RIGHT: lambda state: key_press(state, []),
    }, {"pressed": []})
