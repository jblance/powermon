"""
Test / simulation fixtures for PI30 protocol commands.

These fixtures are:
- non-authoritative
- captured from real devices / firmware
- sometimes incomplete or variant
- intended for mock ports and regression tests

Do NOT rely on them for protocol truth.
"""


from powermon.protocols.model import CommandFixture

# =============================================================================
# QPIGS — inverter status information
# =============================================================================

QPIGS_FIXTURES = [
    CommandFixture(
        description="Normal running, grid available",
        raw_response=b"(000.0 00.0 230.0 49.9 0161 0119 003 460 57.50 012 100 0069 0014 103.8 57.45 00000 00110110 00 00 00856 010\x24\x8c\r",
        notes="Captured from 5kVA unit, firmware 72.70",
    ),
    CommandFixture(
        description="High PV input, load present",
        raw_response=b"(227.2 50.0 230.3 50.0 0829 0751 010 447 54.50 020 083 0054 02.7 323.6 00.00 00000 00010110 00 00 00879 010\xf1\x8c\r",
        notes="Observed during midday PV peak",
    ),
    CommandFixture(
        description="Extended response variant",
        raw_response=b"(227.2 50.0 230.3 50.0 0829 0751 010 447 54.50 020 083 0054 02.7 323.6 00.00 00000 00010110 00 00 00879 010 1 02 123\x1c\x84\r",
        notes="Some firmware variants append extra fields",
    ),
]

# =============================================================================
# QPIRI — inverter configuration settings
# =============================================================================

QPIRI_FIXTURES = [
    CommandFixture(
        description="48V inverter, typical configuration, moderate load",
        raw_response=b"(230.0 21.7 230.0 50.0 21.7 5000 4000 48.0 46.0 42.0 56.4 54.0 "
                     b"0 10 010 1 0 0 6 01 0 0 54.0 0 1\x6F\x7E\r",
        notes="Common reference sample used during early protocol development",
    ),

    CommandFixture(
        description="120V inverter variant, different firmware",
        raw_response=b"(120.0 25.0 120.0 60.0 25.0 3000 3000 48.0 46.0 44.0 58.4 54.4 "
                     b"2 30 060 1 2 0 9 01 0 7 54.0 0 1 000 0\x27\xc9\r",
        notes="Observed on US-market unit; includes extra trailing values",
    ),

    CommandFixture(
        description="24V inverter, low-voltage battery configuration",
        raw_response=b"(230.0 13.0 230.0 50.0 13.0 3000 2400 24.0 23.0 21.0 28.2 27.0 "
                     b"0 30 50 0 2 1 - 01 1 0 26.0 0 0\xb9\xbd\r",
        notes="Battery fields differ significantly for 24V units",
    ),

    CommandFixture(
        description="48V inverter, max charge currents",
        raw_response=b"(230.0 21.7 230.0 50.0 21.7 5000 5000 48.0 47.0 46.5 57.6 57.6 "
                     b"5 30 080 0 1 2 1 01 0 0 52.0 0 1\x03$\r",
        notes="High-current configuration; good stress-case for parsing",
    ),

    CommandFixture(
        description="48V inverter, firmware variant with alternate CRC",
        raw_response=b"(230.0 21.7 230.0 50.0 21.7 5000 5000 48.0 47.0 46.5 57.6 57.6 "
                     b"9 30 080 0 1 2 1 01 0 0 52.0 0 1\x9c\x6f\r",
        notes="CRC differs despite identical payload; confirms CRC is active",
    ),

    CommandFixture(
        description="Large parallel inverter, extended values",
        raw_response=b"(230.0 34.7 230.0 50.0 34.7 8000 8000 48.0 48.0 42.0 54.0 52.5 "
                     b"2 010 030 1 2 2 9 01 0 0 50.0 0 1 480 0 070\xd9`\r",
        notes="Extended parallel configuration; longer payload",
    ),
]
