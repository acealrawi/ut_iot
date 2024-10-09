# pip install bleak


from bleak import BleakScanner
import asyncio
from bleak import BleakClient

thingy52_mac = "XX:XX:XX:XX:XX:XX"  # Replace with your Thingy:52 MAC address

async def run():
    async with BleakClient(thingy52_mac) as client:
        print(f"Connected: {client.is_connected}")

        # Read characteristic (UUID of temperature sensor in Thingy:52)
        temperature_char_uuid = "ef680201-9b35-4933-9b10-52ffa9740042"
        temperature_value = await client.read_gatt_char(temperature_char_uuid)
        print(f"Temperature: {temperature_value}")

        # If you want notifications
        def notification_handler(sender, data):
            print(f"Notification from {sender}: {data}")

        await client.start_notify(temperature_char_uuid, notification_handler)
        await asyncio.sleep(5)
        await client.stop_notify(temperature_char_uuid)

asyncio.run(run())



# Scan for devices to dinf mac address
async def scan():
    devices = await BleakScanner.discover()
    for device in devices:
        print(device)

asyncio.run(scan())


