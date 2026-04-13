@dataclass(frozen=True)
class DalyFrameSpec:
    def encode_request(self, cmd: CommandDefinition, *, params=None, ctx: EncodeContext) -> bytes:
        is_ble = ctx.port_type is PortType.BLE
        source = 0x80 if is_ble else 0x40
        code = int(cmd.request.command_code, 16)

        frame = bytearray([0xA5, source, code, 8]) + bytearray(8)
        frame.append(sum(frame) & 0xFF)
        if not is_ble:
            frame.append(0x0A)
        return bytes(frame)