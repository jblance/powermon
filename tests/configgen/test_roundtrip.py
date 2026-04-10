# tests/configgen/test_roundtrip.py
import io
from ruamel.yaml import YAML  # ty: ignore[unresolved-import]

from powermon.cli.config_generate import generate_base_config
from powermon.config import PowermonConfig

def test_roundtrip_yaml_to_model():
    cfg = generate_base_config()
    data = cfg.model_dump(mode="json", exclude_defaults=True, exclude_none=True)

    # dump to YAML string
    yaml = YAML()
    buf = io.StringIO()
    yaml.dump(data, buf)
    yaml_text = buf.getvalue()

    # load YAML string back to dict
    loaded = yaml.load(io.StringIO(yaml_text))

    # validate back into model
    cfg2 = PowermonConfig.model_validate(loaded)

    assert cfg2.model_dump(mode="json") == PowermonConfig.model_validate(data).model_dump(mode="json")
