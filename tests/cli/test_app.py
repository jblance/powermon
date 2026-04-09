from typer.testing import CliRunner

from powermon.cli.app import create_app
from powermon.cli.deps import Deps


def test_version_command():
    runner = CliRunner()

    deps = Deps(
        translate=lambda s: s,
        version="1.2.3",
        python_version=lambda: "3.12.0",
        list_protocols=lambda: None,
        list_commands=lambda _: None,
        list_formats=lambda: None,
        list_outputs=lambda: None,
        protocol_enum=[],
        get_protocol_definition=lambda _: None,
        config_error_type=Exception,
        deepdiff=lambda *a, **k: {},
        generate_config_file=lambda: None,
        ble_reset=lambda: None,
        ble_scan=lambda **k: None,
    )

    app = create_app(deps)

    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "1.2.3" in result.stdout
    assert "3.12.0" in result.stdout


def test_compare_invokes_compare_logic(monkeypatch):
    runner = CliRunner()

    called = {}

    def fake_compare(spec, deps, cache):
        called["spec"] = spec

    monkeypatch.setattr("powermon.cli.app.compare_protocols", fake_compare)

    deps = Deps(
        translate=lambda s: s,
        version="x",
        python_version=lambda: "x",
        list_protocols=lambda: None,
        list_commands=lambda _: None,
        list_formats=lambda: None,
        list_outputs=lambda: None,
        protocol_enum=[],
        get_protocol_definition=lambda _: None,
        config_error_type=Exception,
        deepdiff=lambda *a, **k: {},
        generate_config_file=lambda: None,
        ble_reset=lambda: None,
        ble_scan=lambda **k: None,
    )

    app = create_app(deps)

    result = runner.invoke(app, ["compare", "pi30", "pi30max"])

    assert result.exit_code == 0
    assert called["spec"] == "pi30,pi30max"