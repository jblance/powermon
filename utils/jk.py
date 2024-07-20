""" test area for using construct lib to decode a jk serial packet """
import math
import datetime
try:
    import construct as cs
except ImportError:
    print("You are missing dependencies")
    print("To install use:")
    print("    python -m pip install 'construct'")

def uptime(byteData):
    """
    Decode 3 hex bytes to a JKBMS uptime
    """
    # Make sure supplied String is the correct length
    # log.debug("uptime defn")
    value = 0
    for x, b in enumerate(byteData):
        # b = byteData.pop(0)
        value += b * 256 ** x
        print(f"Uptime int value {value} for pos {x}")
    print(value)
    daysFloat = value / (60 * 60 * 24)
    days = math.trunc(daysFloat)
    hoursFloat = (daysFloat - days) * 24
    hours = math.trunc(hoursFloat)
    minutesFloat = (hoursFloat - hours) * 60
    minutes = math.trunc(minutesFloat)
    secondsFloat = (minutesFloat - minutes) * 60
    seconds = round(secondsFloat)
    uptime = f"{days}D{hours}H{minutes}M{seconds}S"
    print(f"Uptime result {uptime}")
    return uptime

response1 = b'U\xaa\xeb\x90\x02a6\x0c8\x0c)\x0c:\x0c5\x0c:\x0c8\x0c:\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x009\x0c\x1c\x00\x03\x028\x009\x008\x008\x008\x008\x007\x008\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xdc\x00\x00\x00\x00\x00\xc5a\x00\x00\xb2E\x03\x00\x88\xde\xff\xff\xd4\x00\xca\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0E\x04\x00\x0b\x00\x00\x00\xf2\xe00\x00d\x00\x00\x00\xae\x170\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x01\x00\x00\x00\xfc\x03#\x00*\x00\xca\xfa@@\x00\x00\x00\x00\xc6\t\xa1\x1b\x00\x01\x00\x01\xbb\x05\x00\x00\x8a\xd4O\x00\x00\x00\x00\x00\xdc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xff\x7f\xdc\x0f\x01\x00\x00\x00\x00\x00\x00Q'
response2 = b'U\xaa\xeb\x90\x02\xc1\xac\x0c\xad\x0c\xae\x0c\xb1\x0c\xb1\x0c\xb2\x0c\xae\x0c\xae\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x00\xb0\x0c\x07\x00\x03\x008\x009\x008\x008\x008\x008\x007\x008\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe2\x00\x00\x00\x00\x00\x81e\x00\x00\x8fx\x06\x00\xc0?\x00\x00\xc0\x00\xbe\x00\x00\x00\x00\x00\x00\x00\x00\t\xbfb\x00\x00\xc0E\x04\x00\x0b\x00\x00\x00\x94\r2\x00d\x00\x00\x00\xee\xbc0\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x01\x00\x00\x00\xfc\x03P\x00\x00\x00\xca\xfa@@\x00\x00\x00\x00&\n\x85\x1b\x00\x01\x00\x01\xbc\x05\x00\x00\x07IV\x00\x00\x00\x00\x00\xe2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xff\x7f\xdc\x0f\x01\x00\x00\x00\x00\x00\x00R'
response3 = bytes.fromhex('55aaeb900200120d120d110d110d110d110d110d110d120d110d110d110d110d110d110d110d0000000000000000000000000000000000000000000000000000000000000000ffff0000110d01000003530050004f004a004d004b004d004d0053004e004d004a004c004d00520051000000000000000000000000000000000000000000000000000000000000000000dd000000000017d100000000000000000000c700cd000000000000000064aa9e040080a3040000000000b30c00006400000056a3290001010000000000000000000000000000ff00010000009a030000000060543f4000000000e8140000000101010006000082775c0000000000dd00c700ce009a03533f09007f0000008051010000000000000000000000000000feff7fdd2f0101b0070000003e001016200001059a')
response4 = b'U\xaa\xeb\x90\x02&\xf5\x0c\xfa\x0c\xf9\x0c\x01\r\xf9\x0c\xff\x0c\xf9\x0c\xf9\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x00\xfa\x0c\x0b\x00\x03\x008\x009\x008\x008\x008\x008\x007\x008\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe5\x00\x00\x00\x00\x00\xd3g\x00\x00K7\x10\x00\xfc\x9c\x00\x00\xbd\x00\xb7\x00\x00\x00\x00\x00m\xf8\x02\rX\x89\x00\x00\xc0E\x04\x00\x0e\x00\x00\x00\x8e\xce?\x00d\x00\x00\x00\xc1\x016\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x00\x01\x00\x00\x00\xfc\x03\xc5\x00\x00\x00\xca\xfa@@\xd3\x00\x00\x00a\n\x94\x1b\x00\x01\x00\x01\xbd\x05\x00\x00F\xf9\x8a\x00\x00\x00\x00\x00\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xff\x7f\xdc\x0f\x01\x00\x00\x00\x00\x00\x00\x9a'
response5 = bytes.fromhex('55aaeb900200130d120d120d120d120d120d120d110d110d120d110d110d110d120d120d110d0000000000000000000000000000000000000000000000000000000000000000ffff0000120d02000008530050004f004a004d004b004d004d0053004e004d004a004c004d00520051000000000000000000000000000000000000000000000000000000000000000000ea00000000001dd100000000000000000000d100d80000000000000000632d92040080a30400000000003019000064000000a022410001010000000000000000000000000000ff00010000009a030000000060543f4000000000e914000000010101000600006570470100000000ea00d200d7009a030fbf20007f0000008051010000000000000000000000000000feff7fdd2f0101b00700000093001016200001059a')
response6 = bytes.fromhex('55aaeb900200130d120d120d120d120d120d120d120d110d110d110d120d120d110d110d110d0000000000000000000000000000000000000000000000000000000000000000ffff0000120d02000007530050004f004a004d004b004d004d0053004e004d004a004c004d00520051000000000000000000000000000000000000000000000000000000000000000000ea00000000001fd100000000000000000000d000d80000000000000000632d92040080a30400000000003019000064000000a722410001010000000000000000000000000000ff00010000009a030000000060543f4000000000e91400000001010100060000ad70470100000000ea00d200d7009a0316bf20007f0000008051010000000000000000000000000000feff7fdd2f0101b007000000e9001016200001059a')
response_type01 = bytes.fromhex('55aaeb900100ac0d0000280a00005a0a0000240e0000780d000005000000790d0000500a00007a0d0000160d0000c409000050c30000030000003c000000102700002c0100003c00000005000000d0070000bc02000058020000bc0200005802000038ffffff9cffffffe8030000200300001000000001000000010000000100000080a30400dc0500007a0d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000500000060e3160010023c3218feffffffbfe9010200000000f50010161e00016456')
response_jk04 = b"U\xaa\xeb\x90\x02\xfd\x01\x04\x13@\x81\xbc\x16@E\xd2\x10@\xed\xd4\x16@\xed\xd4\x16@2\x1e\x17@\xa8\x10\x14@\xe3\x7f\x17@\x15\xa4\x16@\xf7)\x16@2\x1e\x17@\xb1\xf4\x0b@2\xa3\x14@\x9eJ\r@\x9e\xc5\x0f@\xa8\x8b\x16@\x9e6\x17@\xc6\x05\x17@\xe3\x7f\x17@Y\xed\x16@\xe3\x7f\x17@\xcf\xdf\x13@Y\xed\x16@2\xa3\x14@\xab\xe5p>Yk2>&\xef\xf6=>\xb84>p\xfc~>\xab9\xbc>\xde\xd3\xb6>25\x80>672>\xaeG\xf7=\x86\xc4\xfa=g,\x02>\xf6&\x02>\x97S\x01>\xd8\x1d\x01>\x94%\x05>JF\x00>\x8f\xd83>\xe0a\x92>\x05\xf2\xaa>\xd2\xbaU>\xad\xc0\xf8=\xee\x88\xf7=\xd5\xa2@>\x00\x00\x00\x00\x92\xf2\x14@P,7>\x00\x00\x00\x00\xff\xff\xff\x00\x07\x0b\x01\x01\x00X\xb6?\x00\x00\x00\x00\x00\x00\x00Z{\xedK@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\xd2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xa0/\x00\x00\x00\x00\x00\x00\x00X*@\x00\x0b"
response_jk04_2 = bytes.fromhex("55aaeb9002ff5b566240e34e62406e6a62404a506240acd7624011d26240bddd62409ad1624044c86240cedc6240ccc7624079e1624057dc624073a262405f80624088c46240000000000000000000000000000000000000000000000000000000000000000013315c3d0636143d26e0113d8021f03c1153363d8980123d7e7c033dac41233d1ad83c3d9d6f4f3d8eb51e3d6a2c293deb28653d189c523da3724e3deb94493d9ab2c23d00000000000000000000000000000000000000000000000000000000000000001aad62400084053c00000000ffff00000b000000000000000000000000000036a3554c40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000be0b54001456a43fb876a43f00a2")
response_type03a = bytes.fromhex("55aaeb9003b54a4b2d42443641323053313050000000342e300000000000342e312e37000000541d1600040000004e6f7468696e67204a4b31000000000031323334000000000000000000000000323030373038000032303036323834303735000000000000496e707574205573657264617461000031323334353600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c4")
response_type03b = bytes.fromhex("55aaeb9003f14a4b2d42324132345300000000000000332e300000000000332e322e330000000876450004000000506f7765722057616c6c203100000000313233340000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c2")
response = response_type03a
print(len(response))

record_01 = cs.Struct(
    "Record_Counter" / cs.Byte,
    "voltage_smart_sleep" / cs.Int32ul,
    "cell_under_voltage_protection" / cs.Int32ul,
    "cell_under_voltage_protection_recovery" / cs.Int32ul,
    "cell_over_voltage_protection" / cs.Int32ul,
    "cell_over_voltage_protection_recovery" / cs.Int32ul,
    "balance_trigger_voltage" / cs.Int32ul,
    "soc_100%_voltage" / cs.Int32ul,
    "soc_0%_voltage" / cs.Int32ul,
    "cell_request_charge_voltage" / cs.Int32ul,
    "cell_request_float_voltage" / cs.Int32ul,
    "power_off_cell_voltage" / cs.Int32ul,
    "continued_charge_current" / cs.Int32ul,
    "charge_ocp_delay_sec" / cs.Int32ul,
    "charge_ocpr_time_sec" / cs.Int32ul,
    "unknown2" / cs.Int32ul,
    "discharge_ocp_delay_sec" / cs.Int32ul,
    "discharge_ocpr_time_sec" / cs.Int32ul,
    "scpr_time_sec" / cs.Int32ul,
    "max_balance_current" / cs.Int32ul,
    "charge_otp_c" / cs.Int32ul,
    "charge_otpr_c" / cs.Int32ul,
    "discharge_otp_c" / cs.Int32ul,
    "discharge_otpr_c" / cs.Int32ul,
    "charge_utp_c" / cs.Int32sl,
    "charge_utpr_c" / cs.Int32sl,
    "mos_otp_c" / cs.Int32ul,
    "mos_otpr_c" / cs.Int32ul,
    "cell_count" / cs.Int32ul,
    "unknown7" / cs.Bytes(4),
    "unknown8" / cs.Bytes(4),
    "unknown9" / cs.Bytes(4),
    "nominal_battery_capacity" / cs.Int32ul,
    "scp_delay_us" / cs.Int32ul,
    "start_balance_voltage" / cs.Int32ul,
    "unknown11" / cs.Bytes(8),
    "unknown12" / cs.Bytes(8),
    "unknown13" / cs.Bytes(8),
    "unknown14" / cs.Bytes(8),
    "unknown15" / cs.Bytes(8),

    "rest" / cs.GreedyBytes,
)

record_02 = cs.Struct(
    "Record_Counter" / cs.Byte,
    "cell_voltage_array" / cs.Array(32, cs.Int16ul),
    "cell_presence" / cs.BitStruct("cells" / cs.Array(32, cs.Enum(cs.Bit, not_present=0, present=1))),
    "Average_Cell_Voltage" / cs.Int16ul,
    "Delta_Cell_Voltage" / cs.Int16ul,
    "cell_highest_voltage" / cs.Byte,
    "cell_lowest_voltage" / cs.Byte,
    "cell_resistance_array" / cs.Array(32, cs.Int16ul),
    "mos_temp" / cs.Int16ul,
    "discard3" / cs.Bytes(4),
    "battery_voltage" / cs.Int32ul,
    "battery_power" / cs.Int32ul,
    "battery_current" / cs.Int32sl,
    "T1" / cs.Int16ul,
    "T2" / cs.Int16ul,
    "discard4" / cs.Bytes(4),
    "balance_current" / cs.Int16sl,
    "discard5" /  cs.Bytes(1),
    "Percent_Remain" / cs.Int8ul,
    "Capacity_Remain" / cs.Int32ul,
    "Nominal_Capacity" / cs.Int32ul,
    "Cycle_Count" / cs.Int32ul,
    "Cycle_Capacity" / cs.Int32ul,
    "discard6" / cs.Bytes(4),
    "uptime" / cs.Int24ul,
    "discard8" / cs.Bytes(8),
    "discard9" / cs.Bytes(8),
    "discard10" / cs.Bytes(8),
    "discard11" / cs.Bytes(8),
    "discard12" / cs.Bytes(8),
    "discard13" / cs.Bytes(8),
    "discard14" / cs.Bytes(8),
    "discard15" / cs.Bytes(8),
    "discard16" / cs.Bytes(8),
    "discard17" / cs.Bytes(8),
    "discard18" / cs.Bytes(8),
    "discard19" / cs.Bytes(8),
    "discard20" / cs.Optional(cs.Bytes(8)),
    "discard21" / cs.Optional(cs.GreedyBytes)
)

record_03 = cs.Struct(
    "Record_Counter" / cs.Byte,
    "device_model" / cs.Bytes(16),
    "hardware_version" / cs.Bytes(8),
    "software_version" / cs.Bytes(8),
    "uptime_seconds" / cs.Int32ul,
    "power_on_times" / cs.Int32ul,
    "device_name" / cs.Bytes(16),
    "device_passcode" / cs.Bytes(16),
    "Manufacturing Date" / cs.Bytes(8),
    "Serial Number" / cs.Bytes(16),
    "User Data" / cs.Bytes(16),
    "Setup Passcode" / cs.Bytes(16),
    "null_padding" / cs.Bytes(165),
    "checksum" / cs.Bytes(1),
)
jk02_32_definition = cs.Struct(
    "header" / cs.Bytes(4),
    "record_type" / cs.Byte,
    "record_decode" / cs.Switch(cs.this.record_type, {1: record_01, 2: record_02, 3: record_03}),
)

jk04_definition = cs.Struct(
    "header" / cs.Bytes(4),
    "record_type" / cs.Byte,
    "record_counter" / cs.Byte,
    "cell_voltage_array" / cs.Array(24, cs.Float32l),
    "cell_resistance_array" / cs.Array(25, cs.Float32l),
    "average_cell_voltage" / cs.Float32l,
    "delta_cell_voltage" / cs.Float32l,
    "unknown1" / cs.Bytes(4),
    "unknown2" / cs.Bytes(4),
    "highest_cell" / cs.Byte,
    "lowest_cell" / cs.Byte,
    "flags" / cs.Bytes(2),
    "unknown3" / cs.Bytes(4),
    "unknown4" / cs.Bytes(4),
    "unknown5" / cs.Bytes(4),
    "unknown6" / cs.Bytes(4),
    "unknown7" / cs.Bytes(4),
    "unknown8" / cs.Bytes(44),
    "uptime_seconds" / cs.Int32ul,
    "unknown9" / cs.Bytes(4),
    "unknown10" / cs.Bytes(4),
    "unknown11" / cs.Bytes(1),
    "checksum" / cs.Bytes(1),

    "rest" / cs.GreedyBytes,
)

result = jk02_32_definition.parse(response)
# print(result)
#result = jk04_definition.parse(response)
print(result)
# print(result.uptime)
# print(uptime(result.uptime))

sec = result.record_decode.uptime_seconds
print(str(datetime.timedelta(seconds = sec)))
exit()


#print(bin(result[0].discard1))
# result = jk02_32_definition.parse(response5)
# result2 = jk02_32_definition.parse(response6)
exit()
# for x in result:
#     match type(result[x]):
#         # case cs.ListContainer:
#         #     print(f"{x}:listcontainer")
#         case cs.Container:
#             pass
#             print(f"{x}:")
#             for y in result[x]:
#                 if y.startswith("discard1"):
#                     print(f"\t{y}: {bin(result[x][y])}")
#         case _:
#             if x == "discard1":
#                 #if result[x] == result2[x]:
#                 #    print(f"{x}: {result[x]} matches")
#                 print(f"{x}bin: {bin(result[x])}")
#             else:
#                 print(f"{x}: {result[x]}")
