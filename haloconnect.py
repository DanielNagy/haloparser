"""
Halo Scan / pairing

This file is covered under the MIT license described in the file LICENSE
"""
import argparse
import time
import asyncio
import logging
import binascii

from bleak import BleakClient, BleakScanner
from pychlorinator.halo_parsers import *


import pychlorinator.chlorinator


logger = logging.getLogger(__name__)


UUID_ASTRALPOOL_SERVICE_2 = "45000001-98b7-4e29-a03f-160174643002"
UUID_SLAVE_SESSION_KEY_2 = "45000001-98b7-4e29-a03f-160174643002"
UUID_MASTER_AUTHENTICATION_2 = "45000002-98b7-4e29-a03f-160174643002"
UUID_TX_CHARACTERISTIC = "45000003-98b7-4e29-a03f-160174643002"
UUID_RX_CHARACTERISTIC = "45000004-98b7-4e29-a03f-160174643002"
ASTRALPOOL_HALO_BLE_NAME = "HCHLOR"

class DeviceNotFoundError(Exception):
    pass


async def halo_ble_client(args: argparse.Namespace, queue: asyncio.Queue):
    #ACCESS_CODE = bytes("xxxx", "utf_8")
    ACCESS_CODE = None

    isPaired = ACCESS_CODE != None

    halo_scan_response = None
    halo_device = None

    while not isPaired:
        logger.info("Scanning for HALO Advertisements...")

        all_devices = await BleakScanner.discover(return_adv=True, timeout=5)
        found_devices = []
        for device, adv in all_devices.values():
               if adv.local_name == ASTRALPOOL_HALO_BLE_NAME:
                found_devices.append([device, adv])
                logger.info(f"Halo Device found: {adv}")
        if len(found_devices) == 0:
            logger.info("No Halo found.")

        if len(found_devices) == 1:
            halo_device = found_devices[0][0]
            manufacturer_data = found_devices[0][1].manufacturer_data
            
            logger.info(f"Halo Scan: {halo_device} {binascii.hexlify(manufacturer_data[1095])}")
            halo_scan_response = ScanResponse(manufacturer_data[1095])
            logger.info(f"Scan response: {vars(halo_scan_response)}")
            logger.info(f"Is Pairable?: {halo_scan_response.isPairable}")

        if halo_scan_response.isPairable:
            ''' Grab Access code from Manufactorer_Data in Advertisement'''
            logger.info(f"Access Code: {halo_scan_response.ByteAccessCode}")
            ACCESS_CODE = halo_scan_response.ByteAccessCode
            isPaired = ACCESS_CODE != None
            ''' save ACCESS_CODE as a const so when plugin starts again, doesnt go through this process?'''




    ''' ASSUME DEVICE IS PAIRED / VALID ACCESS_CODE FOR BELOW TO WORK '''
    device = await BleakScanner.find_device_by_name(
        ASTRALPOOL_HALO_BLE_NAME, cb=dict(use_bdaddr=args.macos_use_bdaddr)
    )
    if device is None:
        logger.error("Could not find Halo named '%s'", args.name)
        raise DeviceNotFoundError

    #logger.info(f"Halo name: {device.name}, Address: {device.address}, meta: {device.metadata}")
    logger.info("connecting to Halo...")

    async def callback_handler(_, data):
        await queue.put((time.time(), data, session_key))

  
    async with BleakClient(device) as client:
        logger.info("connected to Halo...")
        session_key = await client.read_gatt_char(UUID_SLAVE_SESSION_KEY_2)
        print(f"got session key {session_key.hex()}")
        
        await client.start_notify(UUID_TX_CHARACTERISTIC, callback_handler)
        print(f"Turn on notifications for {UUID_TX_CHARACTERISTIC}")

        await client.start_notify(UUID_TX_CHARACTERISTIC, callback_handler)
        print(f"Turn on notifications for {UUID_TX_CHARACTERISTIC}")

        mac = pychlorinator.chlorinator.encrypt_mac_key(session_key, ACCESS_CODE)
        print(f"mac key to write {mac.hex()}")
        await client.write_gatt_char(UUID_MASTER_AUTHENTICATION_2, mac)

        ''' PerformVomitAsync'''
        logger.info("PerformVomitAsync...")
        await client.write_gatt_char(UUID_RX_CHARACTERISTIC, pychlorinator.chlorinator.encrypt_characteristic(bytes([2, 107, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), session_key)) # ReadForCatchAll(107)
        await client.write_gatt_char(UUID_RX_CHARACTERISTIC, pychlorinator.chlorinator.encrypt_characteristic(bytes([2, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), session_key)) # ReadForCatchAll(5)

        while True:
            logger.info("***** Sending Keep Alive")
            await asyncio.sleep(5)
            await client.write_gatt_char(UUID_RX_CHARACTERISTIC, pychlorinator.chlorinator.encrypt_characteristic(bytes([2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), session_key)) # ReadForCatchAll(1) KEEP ALIVE

            logger.info("***** Requesting Additional Stats")
            await client.write_gatt_char(UUID_RX_CHARACTERISTIC, pychlorinator.chlorinator.encrypt_characteristic(bytes([2, 88, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), session_key)) # ReadForCatchAll(600) StatsPage Data
            await client.write_gatt_char(UUID_RX_CHARACTERISTIC, pychlorinator.chlorinator.encrypt_characteristic(bytes([2, 89, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), session_key)) # ReadForCatchAll(601) StatsPage Data
            await client.write_gatt_char(UUID_RX_CHARACTERISTIC, pychlorinator.chlorinator.encrypt_characteristic(bytes([2, 90, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), session_key)) # ReadForCatchAll(602) StatsPage Data
            await client.write_gatt_char(UUID_RX_CHARACTERISTIC, pychlorinator.chlorinator.encrypt_characteristic(bytes([2, 91, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), session_key)) # ReadForCatchAll(603) StatsPage Data
            #await client.write_gatt_char(UUID_RX_CHARACTERISTIC, pychlorinator.chlorinator.encrypt_characteristic(bytes([2, 101, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), session_key)) # ReadForCatchAll(101) Testing request for 101

        await asyncio.sleep(25.0)
        await client.stop_notify(UUID_TX_CHARACTERISTIC)
        # Send an "exit command to the consumer"
        await queue.put((time.time(), None))

    logger.info("disconnected")



async def halo_queue_consumer(queue: asyncio.Queue):
    logger.info("Starting Halo queue consumer")

    def ExtractUnknown():
        logger.debug(f"Unknown {CmdType} {CmdData}")

    def ExtractProfile(): #1
        logger.info(f"ExtractProfile: {vars(DeviceProfileCharacteristic2(CmdData))}")
    def ExtractName(): #6
        logger.info(f"ExtractName {CmdData.decode('utf-8', errors='ignore')}")
    def ExtractTemp(): #9
        logger.info(f"ExtractTemp {vars(TempCharacteristic(CmdData))}")

    def ExtractSettings(): #100
        logger.info(f"ExtractSettings {vars(SettingsCharacteristic2(CmdData))}")
    def ExtractWaterVolume(): #101
        logger.info(f"ExtractWaterVolume {vars(WaterVolumeCharacteristic(CmdData))}")
    def ExtractSetPoint(): #102
        logger.info(f"ExtractSetPoint {vars(SetPointCharacteristic(CmdData))}")
    def ExtractState(): #104
        logger.info(f"ExtractState {vars(StateCharacteristic3(CmdData))}")
    def ExtractCapabilities(): #105
        logger.info(f"ExtractCapabilities {vars(CapabilitiesCharacteristic2(CmdData))}")
    def ExtractMaintenanceState(): #106
        logger.info(f"ExtractMaintenanceState {vars(MaintenanceStateCharacteristic(CmdData))}")
    def ExtractFlexSettings(): #107
        logger.inf(f"ExtractFlexSettings")

    def ExtractEquipmentConfig(): #201
        logger.info(f"ExtractEquipmentConfig {vars(EquipmentModeCharacteristic(CmdData))}")
    def ExtractEquipmentParameter(): #202
        logger.info(f"ExtractEquipmentParameter {vars(EquipmentParameterCharacteristic(CmdData))}")

    def ExtractLightState(): #300
        logger.info(f"ExtractLightState {vars(LightStateCharacteristic(CmdData))}")
    def ExtractLightCapabilities(): #301
        logger.info(f"ExtractLightCapabilities {vars(LightCapabilitiesCharacteristic(CmdData))}")
    def ExtractLightZoneNames(): #302
        logger.info(f"ExtractLightZoneNames {vars(LightSetupCharacteristic(CmdData))}")

    def ExtractTimerCapabilities(): #400
        logger.info(f"ExtractTimerCapabilities")
    def ExtractTimerSetup(): #401
        logger.info(f"ExtractTimerSetup")
    def ExtractTimerState(): #402
        logger.info(f"ExtractTimerState")
    def ExtractTimerConfig(): #403
        logger.info(f"ExtractTimerConfig")

    def ExtractProbeStatistics(): #600
        logger.info(f"ExtractProbeStatistics {vars(ProbeCharacteristic(CmdData))}")
    def ExtractCellStatistics(): #601
        logger.info(f"ExtractCellStatistics {vars(CellCharacteristic2(CmdData))}")
    def ExtractPowerBoardStatistics(): #602
        logger.info(f"ExtractPowerBoardStatistics {vars(PowerBoardCharacteristic(CmdData))}")
    def ExtractInfoLog(): #603
        logger.info(f"ExtractInfoLog")

    def ExtractHeaterCapabilities(): #1100
        logger.info(f"ExtractHeaterCapabilities {vars(HeaterCapabilitiesCharacteristic(CmdData))}")
    def ExtractHeaterConfig(): #1101
        logger.info(f"HeaterConfigCharacteristic {vars(HeaterConfigCharacteristic(CmdData))}")
    def ExtractHeaterState(): #1102
        logger.info(f"ExtractHeaterState {vars(HeaterStateCharacteristic(CmdData))}")
    def ExtractHeaterCooldownState(): #1104
        logger.info(f"ExtractHeaterCooldownState {vars(HeaterCooldownStateCharacteristic(CmdData))}")

    def ExtractSolarCapabilities(): #1200
        logger.info(f"ExtractSolarCapabilities {vars(SolarCapabilitiesCharacteristic(CmdData))}")
    def ExtractSolarConfig(): #1201
        logger.info(f"ExtractSolarConfig {vars(SolarConfigCharacteristic(CmdData))}")
    def ExtractSolarState(): #1202
        logger.info(f"ExtractSolarState {vars(SolarStateCharacteristic(CmdData))}")

    def ExtractGPONames(): #1300
        logger.info(f"ExtractGPONames {vars(GPOSetupCharacteristic(CmdData))}")
    def ExtractRelayNames(): #1301
        logger.info(f"ExtractRelayNames {vars(RelaySetupCharacteristic(CmdData))}")
    def ExtractValveNames(): #1302
        logger.info(f"ExtractValveNames {vars(ValveSetupCharacteristic(CmdData))}")

    cmds = {
        1: ExtractProfile,
        2: ExtractUnknown, # Extract Time (do we care?)
        3: ExtractUnknown, # Extract Date (do we care?)
        5: ExtractUnknown,
        6: ExtractName,
        9: ExtractTemp,
        100: ExtractSettings,
        101: ExtractWaterVolume,
        102: ExtractSetPoint,
        104: ExtractState,
        105: ExtractCapabilities,
        106: ExtractMaintenanceState,
        107: ExtractFlexSettings,
        201: ExtractEquipmentConfig,
        202: ExtractEquipmentParameter,
        300: ExtractLightState,
        301: ExtractLightCapabilities,
        302: ExtractLightZoneNames,
        400: ExtractTimerCapabilities,
        401: ExtractTimerSetup,
        402: ExtractTimerState,
        403: ExtractTimerConfig,
        600: ExtractProbeStatistics,
        601: ExtractCellStatistics,
        602: ExtractPowerBoardStatistics,
        603: ExtractInfoLog,
        1100: ExtractHeaterCapabilities,
        1101: ExtractHeaterConfig,
        1102: ExtractHeaterState,
        1104: ExtractHeaterCooldownState,
        1200: ExtractSolarCapabilities,
        1201: ExtractSolarConfig,
        1202: ExtractSolarState,
        1300: ExtractGPONames,
        1301: ExtractRelayNames,
        1302: ExtractValveNames
    }

    while True:
        # Use await asyncio.wait_for(queue.get(), timeout=1.0) if you want a timeout for getting data.
        epoch, data, session_key = await queue.get()
        if data is None:
            logger.info(
                "Got message from client about disconnection. Exiting consumer loop..."
            )
            break
        else:
            decrypted = pychlorinator.chlorinator.decrypt_characteristic(data, session_key)
            #logger.info("Received data at %s: %r", epoch, binascii.hexlify(decrypted))

            CmdType = int.from_bytes(decrypted[1:3], byteorder='little')
            CmdData = decrypted[3:19]
            #logger.info(f"CMD: {CmdType} DATA: {binascii.hexlify(CmdData)}")

            if CmdType in cmds:
                cmds[CmdType]()







async def main(args: argparse.Namespace):
    queue = asyncio.Queue()
    client_task = halo_ble_client(args, queue)  # Handles outbound BLE messages
    consumer_task = halo_queue_consumer(queue)  # Handles inbound BLE messages (inserted to queue from BLE Callback)

    try:
        await asyncio.gather(client_task, consumer_task)
    except DeviceNotFoundError:
        pass

    logger.info("Main method done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="when true use Bluetooth address instead of UUID on macOS",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="sets the logging level to debug",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main(args))
