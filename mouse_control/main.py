import asyncio
import argparse
import json
import config
import controller

def instantiate_controllers():
    addresses = config.Config().get_or("addresses")
    supported_controllers = [controller.keyboard]
    instantiated_controllers = []

    for address, controller_type in zip(addresses, supported_controllers):
        instantiated_controllers.append(controller_type(address))

    return instantiated_controllers


async def main_handler():
    controllers = instantiate_controllers()
    tasks = [asyncio.create_task(controller.device_scanner()) for controller in controllers]
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
        for task in tasks:
            task.cancel()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='main', description='Mouse controller utilizing external sensors')
    parser.add_argument('--addresses', default='["c9:68:a3:b0:6f:f9"]', type=str, help="JSON array of MAC addresses of sensors")
    parser.add_argument('--execute_every', default=1, type=float, help="Execute every N seconds")
    parser.add_argument('--verbosity', default=0, type=int, help="Logging verbosity mode", choices=[0, 1, 2])

    args = parser.parse_args()

    config.Config({
        "addresses": json.loads(args.addresses),
        "execute_every": args.execute_every,
        "verbosity": args.verbosity,
    })

    asyncio.run(main_handler())
