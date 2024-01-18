import asyncio
from bleak import BleakScanner

# your UUID here:
UUID_ASTRALPOOL_SERVICE = bytes.fromhex("4500000198b74e29a03f160174643002")

async def main():

    ## devices = await BleakScanner.discover(service_uuid=UUID_ASTRALPOOL_SERVICE)
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Device name: {device.name}, Address: {device.address}, meta: {device.metadata}")

asyncio.run(main())