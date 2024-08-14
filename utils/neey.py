import asyncio
import struct
from bleak import BleakClient, BleakScanner

response = bytearray()
def notification_callback(handle, data):
    global response
    print(handle, data)
    print('got', len(data), 'bytes')
    response += data

address = '3C:A5:51:94:41:9F'
msg = bytes.fromhex('aa5511010100140000000000000000000000faff')
#msg = bytes.fromhex('aa5511010200140000000000000000000000fbff')
print(msg)

async def m():
    global response
    print('scanning for device:', address)
    bledevice = await BleakScanner.find_device_by_address(device_identifier=address, timeout=10.0)
    if bledevice is None:
        print(f"device {address} not found")
        exit()
    print(bledevice)
    client = BleakClient(bledevice)
    print('connecting')
    await client.connect()
    print(client.is_connected)
    for _int in client.services.characteristics:
        _char =  client.services.characteristics[_int]
        print(_int, _char.description, _char.properties)
        if 'read' in _char.properties:
            print(_int, await client.read_gatt_char(_int))
    print('start notify char 9')
    response = bytearray()
    await client.start_notify(9,  notification_callback)
    #print('write gatt char 48')
    #await client.write_gatt_char(12, bytearray(b""))
    print('write gatt char 15')
    await client.write_gatt_char(15, msg)
    # sleep until response is long enough 
    while len(response) < 100:
        print('.')
        await asyncio.sleep(0.1)
    #print('sleep 5')
    #await asyncio.sleep(5)
    #print('sleep 5')
    #await asyncio.sleep(5)
    print(response)

asyncio.run(m())


r = bytearray(b'U\xaa\x11\x01\x01\x00d\x00GW-24S4EB\x00\x00\x00\x00\x00\x00\x00HW-2.8.0ZH-1.2.3V1.0.0\x00\x0020220916\x04\x00\x00\x00n\x85?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\xff')


