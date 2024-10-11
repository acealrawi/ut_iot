import asyncio
from bleak import BleakClient
from nordic_uuid import UUID

async def main(address):
    async with BleakClient(address, timeout=20) as client:
        # Connect and pair the device
        await client.pair()
        print("Connected: {0}".format(client.is_connected))
        print("Address: {0}".format(client.address))

        # Retrieve services
        services = await client.get_services()
        print(f"\nServices on the device:")

        # Iterate over each service and characteristic
        for service in services:
            print(f"\nService: {service.uuid} - {service.description}")

            for char in service.characteristics:
                properties = char.properties
                print(f"  Characteristic: {char.uuid} - {char.description} | Properties: {properties}")

                # Check if it's the temperature characteristic
                if char.uuid == str(UUID.TEMPERATURE) and 'read' in properties:
                    try:
                        # Read the temperature data
                        temp_data = await client.read_gatt_char(str(UUID.TEMPERATURE))
                        temperature = parse_temperature_data(temp_data)
                        print(f"    Temperature Data: {temperature} °C")
                    except Exception as e:
                        print(f"    Could not read temperature data: {e}")


# Helper function to parse temperature data (assuming it's in a typical format)
def parse_temperature_data(data):
    # Here, we assume temperature data is a 16-bit little-endian integer (change as necessary)
    temp_int = int.from_bytes(data[0:2], byteorder='little', signed=True)
    temperature = temp_int / 100  # Convert to Celsius (assuming 0.01°C per LSB)
    return temperature


# Example usage
address = "c9:68:a3:b0:6f:f9"
asyncio.run(main(address))
