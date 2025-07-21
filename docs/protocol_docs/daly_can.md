# DALY CAN Communications Protocol

**Version**: 1.0  
**Date**: 2019-06-11  
**Author**: Dongguan Daly Electronics Co., Ltd

---

## Version History

| Serial Num | Description     | Date       | Version |
|------------|-----------------|------------|---------|
| 1          | Initial version | 2019.06.11 | V1.0    |

---

## 1. Physical Layer

- **Interface**: CAN
- **Baud Rate**: 250K

---

## 2. Communication Format

### 2.1 Basic Timing

- All messages are initiated by the host.
- All slaves receive messages and respond only if the slave address matches.
- Only matched slaves are allowed to return data to the host.

### 2.2 Address Assignment

| Module         | Address |
|----------------|---------|
| BMS Master     | `0x01`  |
| Bluetooth App  | `0x80`  |
| GPRS           | `0x20`  |
| Upper Computer | `0x40`  |

### 2.3 CAN Communication Format

#### 2.3.1 Host → Slave

| CAN ID | Data | 
| --- | --- | 
|  `Priority + Data ID + BMS Address + PC Address` </br> `0x18 10 01 40`| 8 bytes | 

#### 2.3.2 Slave → Host

| CAN ID | Data | 
| --- | --- | 
| `Priority + Data ID + PC Address + BMS Address` </br> `0x18 10 40 01` | 8 bytes |

---

## 3. Communication Content Information

Each message uses a unique **Data ID**.

### `0x90` - Total Voltage, Current, SOC

- **Send**: `Byte0~7`: Reserved
- **Receive**:
  - `Byte0~1`: Cumulative total voltage (0.1 V)
  - `Byte2~3`: Gather total voltage (0.1 V)
  - `Byte4~5`: Current (offset 30000, 0.1 A)
  - `Byte6~7`: State of Charge (SOC, 0.1%)

---

### `0x91` - Maximum and Minimum Voltage

- **Send**: `Byte0~7`: Reserved
- **Receive**:
  - `Byte0~1`: Max cell voltage (mV)
  - `Byte2`: Cell number with max voltage
  - `Byte3~4`: Min cell voltage (mV)
  - `Byte5`: Cell number with min voltage

---

### `0x92` - Maximum and Minimum Temperature

- **Send**: `Byte0~7`: Reserved
- **Receive**:
  - `Byte0`: Max temperature (offset 40, °C)
  - `Byte1`: Cell number with max temperature
  - `Byte2`: Min temperature (offset 40, °C)
  - `Byte3`: Cell number with min temperature

---

### `0x93` - MOSFET Charge/Discharge Status

- **Send**: `Byte0~7`: Reserved
- **Receive**:
  - `Byte0`: State (0 = stationary, 1 = charge, 2 = discharge)
  - `Byte1`: Charge MOS status
  - `Byte2`: Discharge MOS status
  - `Byte3`: BMS life (0–255 cycles)
  - `Byte4~7`: Remaining capacity (mAh)

---

### `0x94` - Status Information 1

- **Send**: `Byte0~7`: Reserved
- **Receive**:
  - `Byte0`: Number of battery strings
  - `Byte1`: Number of temperature sensors
  - `Byte2`: Charger status (0 = disconnected, 1 = connected)
  - `Byte3`: Load status (0 = disconnected, 1 = connected)
  - `Byte4`: Bitmask of DI/DO states:
    - Bit 0–3: DI1–DI4
    - Bit 4–7: DO1–DO4
  - `Byte5~7`: Reserved

---

### `0x95` - Cell Voltage (1~48)

- **Send**: `Byte0~7`: Reserved
- **Receive**:
  - Voltage for each cell is 2 bytes (1 mV)
  - Max 96 bytes sent in 16 frames
  - `Byte0`: Frame number (0–15, 0xFF = invalid)
  - `Byte1~6`: Cell voltages
  - `Byte7`: Reserved

---

### `0x96` - Cell Temperature (1~16)

- **Send**: `Byte0~7`: Reserved
- **Receive**:
  - Each temperature is 1 byte (offset 40, °C)
  - Max 21 bytes in 3 frames
  - `Byte0`: Frame number (starts at 0)
  - `Byte1~7`: Temperatures

---

### `0x97` - Cell Balance State (1~48)

- **Send**: `Byte0~7`: Reserved
- **Receive**:
  - Bit0–47: 0 = Closed, 1 = Open (balance state for cells 1–48)
  - Bit48–63: Reserved

---

### `0x98` - Battery Failure Status

- **Send**: `Byte0~7`: Reserved
- **Receive**:

| Byte | Bits | Description |
|------|------|-------------|
| 0 | 0–7 | Cell/Sum voltage high/low levels |
| 1 | 0–7 | Charge/Discharge temperature alarms |
| 2 | 0–7 | Overcurrent, SOC level alarms |
| 3 | 0–7 | Voltage/temperature difference alarms |
| 4 | 0–7 | MOS temp & circuit errors |
| 5 | 0–7 | Hardware errors (AFE, EEPROM, RTC, etc.) |
| 6 | 0–7 | Module/circuit protection faults |
| 7 | 0–7 | Fault code |

See detailed bit mapping for each fault category.

---

## Notes

- All values using offsets (
