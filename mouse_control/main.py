import bluetooth_interface
import asyncio
import argparse
import json
import config
import controller
import bleak

def instantiate_controllers():
    interface = bluetooth_interface.BluetoothInterface()
    addresses = config.Config().get_or("addresses")
    supported_controllers = [controller.mouse, controller.keyboard]
    instantiated_controllers = []

    for address, controller_type in zip(addresses, supported_controllers):
        instantiated_controllers.append(controller_type(address))
        interface.add_callback(instantiated_controllers[-1].advertisement_callback)

    return interface, instantiated_controllers


async def main_handler():

    interface, controllers = instantiate_controllers()
    listener = asyncio.create_task(interface.start())

    execute_every = config.Config().get_or("execute_every")

    try:
        while True:
            try:
                [controller() for controller in controllers]
            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    raise e
                print(f"main_handler :: {e}")
            await asyncio.sleep(execute_every)
    except KeyboardInterrupt:
        print("Main loop interrupted. Exiting...")
    finally:
        listener.cancel()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='main', description='Mouse controller utilizing external sensors')
    parser.add_argument('--addresses', default='["c9:68:a3:b0:6f:f9", "c7:d8:23:ed:7f:a5"]', type=str, help="JSON array of MAC addresses of sensors")
    parser.add_argument('--execute_every', default=1, type=float, help="Execute every N seconds")
    parser.add_argument('--verbosity', default=0, type=int, help="Logging verbosity mode", choices=[0, 1, 2])

    args = parser.parse_args()

    config.Config({
        "addresses": json.loads(args.addresses),
        "execute_every": args.execute_every,
        "verbosity": args.verbosity,
    })

    asyncio.run(main_handler())
