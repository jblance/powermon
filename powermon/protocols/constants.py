""" protocol constants """
BATTERY_TYPES = [
    "AGM",
    "Flooded",
    "User",
    "Pylontech",
    "Shinheung",
    "WECO",
    "Soltaro",
    "TBD",
    "LIb-protocol compatible",
    "3rd party Lithium"
]

CHARGER_SOURCE_PRIORITIES = [
    "Utility first",
    "Solar first",
    "Solar + Utility",
    "Solar only"
]

OUTPUT_MODES = [
    "single machine",
    "parallel",
    "Phase 1 of 3 phase",
    "Phase 2 of 3 phase",
    "Phase 3 of 3 phase",
    "Phase 1 of 2 phase",
    "Phase 2 of 2 phase"
]

OUTPUT_SOURCE_PRIORITIES = [
    "Utility > Solar > Battery",
    "Solar > Utility > Battery",
    "Solar > Battery > Utility"
]
