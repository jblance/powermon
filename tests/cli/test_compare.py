import rich
from types import SimpleNamespace

from powermon.cli.compare import compare_protocols


# ----------------------------------------------------------------------
# Test doubles
# ----------------------------------------------------------------------

class FakeProtocol:
    def __init__(self, commands: dict):
        self.command_definitions = commands


class FakeCommand:
    def __init__(self, **fields):
        for k, v in fields.items():
            setattr(self, k, v)

    def reading_definition_count(self) -> int:
        return 0

    @property
    def reading_definitions(self):
        return {}


def fake_deepdiff(a, b, **_):
    """Return empty when equal, non-empty when different."""
    return {} if a == b else {"diff": True}


class FakeDeps(SimpleNamespace):
    pass


# ----------------------------------------------------------------------
# Helper to capture rich.print output
# ----------------------------------------------------------------------

def run_compare_and_capture(console, monkeypatch, spec, proto_a, proto_b) -> str:
    """
    Force rich.print() to write to our test console and return captured output.
    """
    monkeypatch.setattr("powermon.cli.compare.print", console.print)

    deps = FakeDeps(
        deepdiff=fake_deepdiff,
        config_error_type=Exception,
    )

    def cached_protocol(name: str):
        if name == "a":
            return proto_a
        if name == "b":
            return proto_b
        raise KeyError(name)

    compare_protocols(spec, deps, cached_protocol)
    return console.export_text()


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_removed_field_is_marked_removed(console, monkeypatch):
    """
    If Protocol A has a value and Protocol B does not,
    the state MUST be ➖ Removed (direction: A → B).
    This locks the aliases regression you fixed.
    """
    proto_a = FakeProtocol(
        {
            "QID": FakeCommand(
                aliases=["get_id", "default"],
                test_responses=[],
            )
        }
    )

    proto_b = FakeProtocol(
        {
            "QID": FakeCommand(
                aliases=None,
                test_responses=[],
            )
        }
    )

    output = run_compare_and_capture(
        console,
        monkeypatch,
        "a,b:QID",
        proto_a,
        proto_b,
    )

    assert "aliases" in output
    assert "➖ Removed" in output
    assert "➕ Added" not in output


def test_added_field_is_marked_added(console, monkeypatch):
    """
    If Protocol B has a metadata field and Protocol A does not,
    the state MUST be ➕ Added.
    """
    proto_a = FakeProtocol(
        {
            "CMD": FakeCommand(
                aliases=None,
                test_responses=[],
            )
        }
    )

    proto_b = FakeProtocol(
        {
            "CMD": FakeCommand(
                aliases=["new_alias"],
                test_responses=[],
            )
        }
    )

    output = run_compare_and_capture(
        console,
        monkeypatch,
        "a,b:CMD",
        proto_a,
        proto_b,
    )

    assert "aliases" in output
    assert "➕ Added" in output
    assert "➖ Removed" not in output


def test_match_is_marked_match(console, monkeypatch):
    """
    Identical values on both sides must be marked ✅ Match.
    """
    proto = FakeProtocol(
        {
            "CMD": FakeCommand(
                foo="same",
                test_responses=[],
            )
        }
    )

    output = run_compare_and_capture(
        console,
        monkeypatch,
        "a,a:CMD",
        proto,
        proto,
    )

    assert "✅ Match" in output
    assert "❌ Changed" not in output
    assert "➕ Added" not in output
    assert "➖ Removed" not in output
