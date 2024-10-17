import asyncio
import argparse
import bleak
import json
import config
import copy
import pyautogui
import math


def parse_data(data):
    result = ""

    for service_id, service_data in data.service_data.items():

        parts = service_data.split(b'\x00\x00')[-1]
        extracted_value = parts.split(b';')[0]
        result = extracted_value.decode('utf-8')

    if result == "":
        raise RuntimeError("failed to extract any data!")

    return result


async def device_scanner(address, shared_data):
    scan_every = config.Config().get("scan_every")
    scanner = bleak.BleakScanner()

    # callback for when we get data
    def advertisement_callback(device, advertisement_data):
        if device.address.lower() == address.lower():
            try:
                shared_data[address] = parse_data(advertisement_data)
            except Exception as e:
                print(f"advertisement_callback :: {address} :: {e}")

    scanner.register_detection_callback(advertisement_callback)
    await scanner.start()

    # loop forever until we get ctrl+c
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print(f"Scan interrupted for {address}. Stopping...")
    finally:
        await scanner.stop()


async def main_handler():
    sensors = config.Config().get("sensors")
    execute_every = config.Config().get("execute_every")
    callback = config.Config().get("callback")

    shared_data = {}
    tasks = [asyncio.create_task(device_scanner(sensor, shared_data)) for sensor in sensors]

    try:
        while True:
            try:
                local_copy = copy.deepcopy(shared_data)  # perform local data copy
                shared_data.clear()  # clear last outputs
                callback(local_copy)  # invoke user supplied callback
            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    raise e # propagate keyboard interrupts
                print(f"main_handler :: {e}")

            await asyncio.sleep(execute_every)
    except KeyboardInterrupt:
        print("Main loop interrupted. Exiting...")
    finally:
        for task in tasks:
            task.cancel()


diagonal = 100
off_diagonal = math.sqrt(math.pow(diagonal, 2) + math.pow(diagonal, 2))

actions = {
    "North": lambda: pyautogui.moveRel(0, -diagonal, duration=1),
    "South": lambda: pyautogui.moveRel(0, diagonal, duration=1),
    "East": lambda: pyautogui.moveRel(diagonal, 0, duration=1),
    "West": lambda: pyautogui.moveRel(-diagonal, 0, duration=1),
    "NE": lambda: pyautogui.moveRel(off_diagonal, -off_diagonal, duration=1),
    "SE": lambda: pyautogui.moveRel(off_diagonal, off_diagonal, duration=1),
    "SW": lambda: pyautogui.moveRel(-off_diagonal, off_diagonal, duration=1),
    "NW": lambda: pyautogui.moveRel(-off_diagonal, -off_diagonal, duration=1)
}

def main(data):

    # for now lets just invoke all actions
    for address, action in data.items():
        print(f"{address} :: {action}")
        actions[action]()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='controller', description='Mouse controller utilizing external sensors')
    parser.add_argument('--sensors', default='["c9:68:a3:b0:6f:f9"]', type=str, help="JSON array of MAC addresses of sensors")
    parser.add_argument('--execute_every', default=1, type=float, help="Execute every N seconds")

    args = parser.parse_args()

    config.Config({
        "sensors": json.loads(args.sensors),
        "execute_every": args.execute_every,
        "callback": main # main callback function
    })

    asyncio.run(main_handler())
