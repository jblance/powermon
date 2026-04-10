# tests/configgen/test_generate_base.py
from powermon.cli.config_generate import generate_base_config
from powermon._config import PowermonConfig

def test_generate_base_config_validates():
    cfg = generate_base_config()
    assert isinstance(cfg, PowermonConfig)

    # Pydantic v2: validate a dict representation again (should always succeed)
    data = cfg.model_dump(mode="json")
    cfg2 = PowermonConfig.model_validate(data)
    assert cfg2.model_dump(mode="json") == data