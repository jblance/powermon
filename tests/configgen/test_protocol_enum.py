# tests/configgen/test_protocol_enum.py
from powermon.ports import MockPortConfig
from powermon.protocols import ProtocolType 

def test_protocol_enum_serializes_to_string():
    port = MockPortConfig(protocol=ProtocolType.PI30)
    dumped = port.model_dump(mode="json")
    assert dumped["protocol"] == "pi30"  # assuming enum values are lowercase tokens

def test_protocol_accepts_string_token():
    port = MockPortConfig.model_validate({"type": "mock", "protocol": "pi30"})
    # should be a ProtocolType instance in-memory
    assert str(port.protocol) in ("pi30", "ProtocolType.PI30")