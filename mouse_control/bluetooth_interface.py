import config
import asyncio
import bleak


class BluetoothInterface:
    def __init__(self):
        self.interface = bleak.BleakScanner()
        self.callbacks = []
        self.verbosity = config.Config().get_or("verbosity", 0)

    def add_callback(self, function):
        self.callbacks.append(function)

    async def start(self):

        def forward_data(device, advertisement_data):
            for callback in self.callbacks:
                callback(device, advertisement_data)

        self.interface.register_detection_callback(forward_data)
        await self.interface.start()

        try:
            while True:
                if self.verbosity > 1:
                    print("bluetooth_interface :: going to sleep")
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            if self.verbosity > 0:
                print("bluetooth_interface :: scanning interrupted")
        finally:
            await self.interface.stop()
