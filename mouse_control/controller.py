import config
import asyncio
import bleak
import pyautogui
import math

class Controller:

    def __init__(self, name, address, actions):
        self.name = name
        self.address = address
        self.actions = actions
        self.current_action = None
        self.verbosity = config.Config().get_or("verbosity", 0)

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

    async def device_scanner(self):
        scanner = bleak.BleakScanner()

        # callback for when we get data
        def advertisement_callback(device, advertisement_data):
            if device.address.lower() == self.address.lower():
                try:
                    if self.verbosity > 1:
                        print(f"{self.name} :: {self.address} :: advertisement_callback :: {advertisement_data}")
                    self.current_action = self._parse_data(advertisement_data)
                except Exception as e:
                    if self.verbosity > 0:
                        print(f"{self.name} :: {self.address} :: advertisement_callback :: {e}")

        scanner.register_detection_callback(advertisement_callback)
        await scanner.start()

        # loop forever until we get ctrl+c
        try:
            while True:
                if self.verbosity > 1:
                    print(f"{self.name} :: {self.address} :: going to sleep")
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            if self.verbosity > 0:
                print(f"{self.name} :: {self.address} :: scanning interrupted")
        finally:
            await scanner.stop()


    def __call__(self):

        if self.current_action is None:
            return

        if self.verbosity > 0:
            print(f"{self.name} :: {self.address} :: executing action for {self.current_action}")

        self.actions[self.current_action]()
        self.current_action = None


def mouse(address):
    off_diagonal = 10
    diagonal = math.sqrt(math.pow(off_diagonal, 2) + math.pow(off_diagonal, 2))
    return Controller("mouse", address, {
        "North": lambda: pyautogui.moveRel(0, -off_diagonal, duration=1),
        "South": lambda: pyautogui.moveRel(0, off_diagonal, duration=1),
        "East": lambda: pyautogui.moveRel(off_diagonal, 0, duration=1),
        "West": lambda: pyautogui.moveRel(-off_diagonal, 0, duration=1),
        "NE": lambda: pyautogui.moveRel(diagonal, -diagonal, duration=1),
        "SE": lambda: pyautogui.moveRel(diagonal, diagonal, duration=1),
        "SW": lambda: pyautogui.moveRel(-diagonal, diagonal, duration=1),
        "NW": lambda: pyautogui.moveRel(-diagonal, -diagonal, duration=1)
    })

def keyboard(address):
    return Controller("keyboard", address, {
        "North": lambda: pyautogui.hold('w'),
        "South": lambda: pyautogui.hold('s'),
        "East": lambda: pyautogui.hold('d'),
        "West": lambda: pyautogui.hold('a'),
        "NE": lambda: pyautogui.hold(['w', 'd']),
        "SE": lambda: pyautogui.hold(['s', 'd']),
        "SW": lambda: pyautogui.hold(['s', 'a']),
        "NW": lambda: pyautogui.hold(['w', 'a'])
    })
