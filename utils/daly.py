import asyncio
import struct

result_208=bytearray(b'\xa5\x01\x95\x08\x01\x0c\x86\x0c\x8b\x0c\x99\x00\x12\xa5\x01\x95\x08\x02\x0c\x86\x0c\x86\x0c\x82\x00\xf7\xa5\x01\x95\x08\x03\x0c\x8d\x0cy\x0c\x8e\x00\xfe\xa5\x01\x95\x08\x04\x0c\x83\x0c\x95\x0c\x85\x00\x08\xa5\x01\x95\x08\x05\x0c\x8a\x0c\x8a\x0c\x9b\x00\x1b\xa5\x01\x95\x08\x06\x0cx\x00\x00\x00\x00\x00\xcd\xa5\x01\x95\x08\x07\x00\x00\x00\x00\x00\x00\x00J\xa5\x01\x95\x08\x08\x00\x00\x00\x00\x00\x00\x00K\xa5\x01\x95\x08\t\x00\x00\x00\x00\x00\x00\x00L\xa5\x01\x95\x08\n\x00\x00\x00\x00\x00\x00\x00M\xa5\x01\x95\x08\x0b\x00\x00\x00\x00\x00\x00\x00N\xa5\xa8\x00@\x00d @\x00\r0\x00\x00d @\x00\xc7Z\x01\x00m2\x00\x00d\xa5\x01\x95\x08\x0e\x00\x00\x00\x00\x00\x00\x00Q\xa5\x01\x95\x08\x0f\x00\x00\x00\x00\x00\x00\x00R\xa5\x01\x95\x08\x10\x00\x00\x00\x00\x00\x00\x00S')
result_205=bytearray(b'\xa5\x01\x95\x08\x01\x0c\x8f\x0c\x7f\x0c\xa5\x01\x95\x08\x02\x0c\x8b\x0c\x90\x0ct\x00\xf8\xa5\x01\x95\x08\x03\x0c\x8a\x0c\x7f\x0c\x97\x00\n\xa5\x01\x95\x08\x04\x0cx\x0c\x92\x0c\x8b\x00\x00\xa5\x01\x95\x08\x05\x0c\x92\x0c\x8a\x0c\x98\x00 \xa5\x01\x95\x08\x06\x0c{\x00\x00\x00\x00\x00\xd0\xa5\x01\x95\x08\x07\x00\x00\x00\x00\x00\x00\x00J\xa5\x01\x95\x08\x08\x00\x00\x00\x00\x00\x00\x00K\xa5\x01\x95\x08\t\x00\x00\x00\x00\x00\x00\x00L\xa5\x01\x95\x08\n\x00\x00\x00\x00\x00\x00\x00M\xa5\x01\x95\x08\x0b\x00\x00\x00\x00\x00\x00\x00N\xa5\x01\x95\x08\xa8\x00@\x00p$@\x00\r0\x00\x00p$@\x00\xc8;\x01\x00m2\x00\x00p$@\x00S1\x00\x00\x00\x00\x00\x00\xa8\x00@\x00\x07\x00\x00\x000\x00@\x00\xa5\x01\x95\x08\x10\x00\x00\x00\x00\x00\x00\x00S')
response = bytearray()
def notification_callback(handle, data):
  global response
  # print(handle, data)
  print('got', len(data), 'bytes')
  response += data

address = '66:66:18:01:09:18'
message = bytearray(b'\xa5\x80\x95\x08\x00\x00\x00\x00\x00\x00\x00\x00\xc2')
message_soc = bytearray(b'\xa5\x80\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\xbd')

def parse2(response):
  responses = response.split(b'\xa5\x01\x95\x08')
  for resp in responses:
    print(len(resp), resp)
    resp = resp[1:7]
    structure = '>3h'
    print(len(resp), resp)
    if len(resp) < 5:
      continue
    if len(resp) == 5:
      resp.append(resp[3])
      print(resp)
    result = (struct.unpack(structure, resp))
    print(result)

from bleak import BleakClient, BleakScanner
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
  print('start notify')
  response = bytearray()
  await client.start_notify(17,  notification_callback)
  print('write gatt char 48')
  await client.write_gatt_char(48, bytearray(b""))
  print('write gatt char 15')
  await client.write_gatt_char(15, message)
  # sleep until response is long enough 
  while len(response) < 201:
    print('.')
    await asyncio.sleep(0.1)
  #print('sleep 5')
  #await asyncio.sleep(5)
  #print('sleep 5')
  #await asyncio.sleep(5)
  print(response)
  for x in range(int(len(response)/13)):
    resp = response[:13]
    response = response[13:]
    print(len(resp), resp)
    result = (struct.unpack('>x x c b b 3h x x', resp))
    if result[0] == b'\x95':
      print(result[3], result[4], result[5])
  #print(len(response))

  # response = b''
  # await client.write_gatt_char(15, message_soc)
  # # sleep until response is long enough
  # #while len(response) < 201:
  # #  print('.')
  # await asyncio.sleep(5.1)
  # print(response)

asyncio.run(m())
