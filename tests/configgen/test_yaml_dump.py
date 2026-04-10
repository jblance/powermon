# tests/configgen/test_yaml_dump.py
import io
from ruamel.yaml import YAML  # ty: ignore[unresolved-import]

from powermon.cli.config_generate import generate_base_config

def dump_yaml(data: dict) -> str:
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    buf = io.StringIO()
    yaml.dump(data, buf)
    return buf.getvalue()

def test_yaml_dump_has_expected_keys():
    cfg = generate_base_config()
    data = cfg.model_dump(mode="json", exclude_defaults=False, exclude_none=True)
    text = dump_yaml(data)

    assert "config_version:" in text
    assert "devices:" in text
    assert "actions:" in text
    assert "port:" in text