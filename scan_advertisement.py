import asyncio
from bleak import BleakScanner

# Function to scan for the specified MAC address
async def scan_for_specific_device(address):
    scanner = BleakScanner()

    def advertisement_callback(device, advertisement_data):
        if device.address.lower() == address.lower():
            print(f"Advertisement from {device.address}: {advertisement_data}")

    scanner.register_detection_callback(advertisement_callback)
    await scanner.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Scan interrupted. Stopping...")
    finally:
        await scanner.stop()


address = "c9:68:a3:b0:6f:f9"
asyncio.run(scan_for_specific_device(address))