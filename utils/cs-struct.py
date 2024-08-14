try:
    import construct as cs
except ImportError:
    print("You are missing dependencies")
    print("To install use:")
    print("    python -m pip install 'construct'")

response = b"\xa5\x01\x95\x08\x01\x0c\xfc\r\x10\r\x0f\x89\x0e\xa5\x01\x95\x08\x02\r3\x0c\xb7\r8\x89\x16\xa5\x01\x95\x08\x03\r\x10\r\x0f\r\x0e\x89#\xa5\x01\x95\x08\x04\r\x10\r\x10\r\x10\x89\'\xa5\x01\x95\x08\x05\r\x10\r\x0f\r\x10\x89\'\xa5\x01\x95\x08\x06\r\x0c\x00\x00\x00\x00\x89\xeb\xa5\x01\x95\x08\x07\x00\x00\x00\x00\x00\x00\x89\xd3\xa5\x01\x95\x08\x08\x00\x00\x00\x00\x00\x00\x89\xd4\xa5\x01\x95\x08\t\x00\x00\x00\x00\x00\x00\x89\xd5\xa5\x01\x95\x08\n\x00\x00\x00\x00\x00\x00\x89\xd6\xa5\x01\x95\x08\x0b\x00\x00\x00\x00\x00\x00\x89\xd7\xa5\xa8\x00@\x00\x00 @\x00\r0\x00\x00\x00 @\x00\x87K\x00\x00m2\x00\x00\x00 @\x00S1\x00\x00\x00\x00\x00\x00\xa8\x00\xa5\x01\x95\x08\x0f\x00\x00\x00\x00\x00\x00\x89\xdb\xa5\x01\x95\x08\x10\x00\x00\x00\x00\x00\x00\x89\xdc"
soc_response = b"\xa5\x01\x90\x08\x02\x10\x00\x00uo\x03\xbc\xf3"

print(response.count(b"\xa5"))
print(len(response))

voltage_construct = cs.Struct(
    "cell_voltages" / cs.Array(14, cs.Struct(
        "start_flag" / cs.Bytes(1),
        "module_address" / cs.Bytes(1),
        "command_id" / cs.Bytes(1),
        "data_length" / cs.Byte,
        "frame_number" / cs.Byte,
        "cell_voltage_array" / cs.Array(3, cs.Int16ub),
        "reserved" / cs.Bytes(1),
        "checksum" / cs.Bytes(1),
    )),
)

soc_construct = cs.Struct(
    "start_flag" / cs.Bytes(1),
    "module_address" / cs.Bytes(1),
    "command_id" / cs.Bytes(1),
    "data_length" / cs.Byte,
    "battery_voltage" / cs.Int16ub,
    "acquistion_voltage" / cs.Int16ub,
    "current" / cs.Int16ub,
    "soc" / cs.Int16ub,
    "checksum" / cs.Bytes(1)
)

result = voltage_construct.parse(response)
# result = soc_construct.parse(soc_response)
print('cell_voltages' in result)
print(result.cell_voltages[0])
# for i, x in enumerate(result):
#     print(i, x, result[x])
