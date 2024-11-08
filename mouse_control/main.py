import bluetooth_interface
import asyncio
import argparse
import json
import config
import controller
import bleak
import widget

def instantiate_controllers():
    interface = bluetooth_interface.BluetoothInterface()
    addresses = config.Config().get_or("addresses")
    supported_controllers = [controller.mouse, controller.movement, controller.actions]
    #supported_controllers = [controller.actions]
    instantiated_controllers = []

    for address, controller_type in zip(addresses, supported_controllers):
        instantiated_controllers.append(controller_type(address))
    
        interface.add_callback(instantiated_controllers[-1].advertisement_callback)

    return interface, instantiated_controllers


async def main_handler():
    execute_every = config.Config().get_or("execute_every", 1)
    gui = config.Config().get_or("gui", False)
    max_history = max(config.Config().get_or("history", 3), 3)

    interface, controllers = instantiate_controllers()
    action_widget = widget.ActionWidget(controllers, max_history) \
        if gui else widget.NullWidget(controllers, max_history)

    listener = asyncio.create_task(interface.start())
    gui = asyncio.create_task(widget.widget_update_loop(action_widget))

    try:
        while True:
            try:
                action_widget()
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
        gui.cancel()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='main', description='Mouse controller utilizing external sensors')
    parser.add_argument('--addresses', default='["c7:d8:23:ed:7f:a5"]', type=str, help="JSON array of MAC addresses of sensors")
    parser.add_argument('--execute_every', default=1, type=float, help="Execute every N seconds")
    parser.add_argument('--verbosity', default=0, type=int, help="Logging verbosity mode", choices=[0, 1, 2])
    parser.add_argument('--gui', action=argparse.BooleanOptionalAction, help="Enable or disable GUI")
    parser.add_argument('--history', default=40, type=int, help="Plot history length")

    args = parser.parse_args()

    config.Config({
        "addresses": json.loads(args.addresses),
        "execute_every": args.execute_every,
        "verbosity": args.verbosity,
        "gui": args.gui,
        "history": args.history
    })

    asyncio.run(main_handler())
