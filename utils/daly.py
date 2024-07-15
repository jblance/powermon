import asyncio
import struct
response = bytearray()
def notification_callback(handle, data):
  global response
  # print(handle, data)
  print('got', len(data), 'bytes')
  response += data

address = '66:66:18:01:09:18'
message = bytearray(b'\xa5\x80\x95\x08\x00\x00\x00\x00\x00\x00\x00\x00\xc2')
from bleak import BleakClient
client = BleakClient(address)
async def m():
  global response
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

asyncio.run(m())
