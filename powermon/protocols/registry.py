"""
Protocol registry.

The registry is responsible for:
  - enumerating known protocol definitions
  - resolving protocol identity (ProtocolType)
  - resolving human-facing selectors to canonical commands

It does NOT:
  - execute commands
  - schedule tasks
  - read/write from ports
"""

from __future__ import annotations

from typing import Iterable, Mapping

from powermon.protocols.model import (
    ProtocolDefinition,
    SelectorTarget,
)


class ProtocolRegistry:
    """
    Central registry of protocol definitions.

    This is a thin lookup layer only.
    """

    def __init__(self, protocols: Iterable[ProtocolDefinition]):
        self._by_type: dict[object, ProtocolDefinition] = {}
        self._by_id: dict[str, ProtocolDefinition] = {}

        for proto in protocols:
            # Register by canonical protocol_type
            if proto.protocol_type in self._by_type:
                raise ValueError(f"Duplicate protocol_type: {proto.protocol_type}")
            self._by_type[proto.protocol_type] = proto

            # Register by wire/descriptive protocol_id (case-insensitive)
            proto_id = proto.protocol_id.lower()
            if proto_id in self._by_id:
                raise ValueError(f"Duplicate protocol_id: {proto.protocol_id}")
            self._by_id[proto_id] = proto

    # ------------------------------------------------------------------
    # Protocol lookup
    # ------------------------------------------------------------------

    def get(self, protocol_type: object) -> ProtocolDefinition:
        """
        Retrieve a ProtocolDefinition by canonical protocol_type.
        """
        try:
            return self._by_type[protocol_type]
        except KeyError as exc:
            raise KeyError(f"Unknown protocol_type: {protocol_type}") from exc

    def get_by_id(self, protocol_id: str) -> ProtocolDefinition:
        """
        Retrieve a ProtocolDefinition by wire/descriptive protocol_id.
        """
        try:
            return self._by_id[protocol_id.lower()]
        except KeyError as exc:
            raise KeyError(f"Unknown protocol_id: {protocol_id}") from exc

    def list_protocols(self) -> list[ProtocolDefinition]:
        """
        Return all registered protocol definitions.
        """
        return list(self._by_type.values())

    # ------------------------------------------------------------------
    # Selector resolution
    # ------------------------------------------------------------------

    def resolve_selector(
        self,
        protocol_type: object,
        token: str,
    ) -> SelectorTarget:
        """
        Resolve a human-facing selector token to a SelectorTarget
        within the context of a protocol.

        Examples:
          - "QID"
          - "serial_number"
          - "battery_voltage"
          - "discharge_voltage"
        """
        proto = self.get(protocol_type)
        key = token.lower()

        try:
            return proto.selectors[key]
        except KeyError as exc:
            raise KeyError(
                f"Unknown selector '{token}' for protocol {proto.protocol_id}"
            ) from exc

    # ------------------------------------------------------------------
    # Command resolution helpers
    # ------------------------------------------------------------------

    def resolve_command(
        self,
        protocol_type: object,
        token: str,
    ):
        """
        Resolve a selector token to a concrete CommandDefinition
        and optional reading/parameter context.

        Returns:
          (command_definition, selector_target)
        """
        proto = self.get(protocol_type)
        selector = self.resolve_selector(protocol_type, token)

        try:
            command = proto.commands[selector.command_id]
        except KeyError as exc:
            # Defensive: protocol definition is internally inconsistent
            raise KeyError(
                f"Protocol {proto.protocol_id} missing command {selector.command_id}"
            ) from exc

        return command, selector

    # ------------------------------------------------------------------
    # Introspection helpers (useful for CLI / docs / completion)
    # ------------------------------------------------------------------

    def list_commands(self, protocol_type: object):
        """
        List all commands for a protocol.
        """
        return self.get(protocol_type).commands.values()

    def list_selectors(self, protocol_type: object) -> Mapping[str, SelectorTarget]:
        """
        List all selectors for a protocol.
        """
        return self.get(protocol_type).selectors
