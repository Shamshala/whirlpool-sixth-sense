"""Whirlpool dishwasher appliance.

## Attribute key investigation (DEX decompilation completed 2026-04-08)

The Android app uses two independent API stacks:

1. **REST shadow API** (flat key-value pairs) – this is what the whirlpool-sixth-sense
   Python library reads.  Keys follow the pattern ``{CavityPrefix}_{SubcategoryName}``
   e.g. ``Cavity_CycleStatusMachineState``.  For dishwashers the cavity prefix is
   ``DishCavity``.

2. **IoT MQTT library** (nested camelCase JSON) – used exclusively by the Android app.
   Keys confirmed from ``Constants.DishConstants`` and ``DishCavityState.setState()``:
   ``applianceState``, ``cycleName``, ``doorStatus``, ``highTemp``, ``heatedDry``,
   ``ecoDry``, ``extraDry``, ``silent``, ``turbo``, ``halfLoad``, ``saniRinse``,
   ``powerClean``, ``detergent``, ``steam``, ``bottleWashZone``, ``tubeWashZone``,
   ``wash3D``, ``timeShortening``, ``powerBoost``, ``childLock``,
   ``cartridge`` → {``lowLevel``, ``emptyLevel``, ``percentageLevel``,
   ``cartridgeInserted``, ``cartridgeDoorClosed``}.

These two key formats are **different**; the camelCase IoT keys cannot be used directly
in the REST shadow API.  The REST shadow keys for dishwashers are **still unconfirmed**
and require validation via live packet capture against a real connected dishwasher.

The keys below are inferred from the washer/dryer convention (``Cavity_`` prefix for
shared attributes, ``DishCavity_`` for dishwasher-specific ones) and from the
``DishAttributeName`` enum in the APK (keys: ``MachineState``, ``TimeRemaining``,
``DoorOpen``, ``ControlLock``, ``QuietModeEnabled``, ``CartridgeLowLevel``, …).

⚠ The ``cartridge`` feature is an **auto-dosing detergent cartridge** (Whirlpool EMEA
detergent pod system), NOT a traditional rinse-aid reservoir.

Covers DDM model keys:
  DDM_DISHWASHER_MIRA_V1
  DDM_DISHWASHER_MIRA_COMBO_V1
  DDM_DISHWASHER_WHR_ODRA_NEBULA_V1
  DDM_DISHWASHER_BAU_ODRA_NEBULA_V1
"""

import logging
from enum import Enum

from .appliance import Appliance

LOGGER = logging.getLogger(__name__)

# ── Machine state (shared Cavity_ prefix, same as washer/dryer) ──────────────
# Inferred from washer pattern; REST API keys still unconfirmed for dishwashers.
ATTR_MACHINE_STATE = "Cavity_CycleStatusMachineState"          # unconfirmed
ATTR_TIME_REMAINING = "Cavity_TimeStatusEstTimeRemaining"       # unconfirmed
ATTR_DOOR_OPEN = "Cavity_OpStatusDoorOpen"                      # unconfirmed

# ── Dishwasher-specific attributes ───────────────────────────────────────────
# DishAttributeName enum keys (APK-confirmed): "OdometerStatus", "ControlLock",
# "QuietModeEnabled", "CartridgeLowLevel", "CartridgeEmptyLevel",
# "CartridgeInserted", "CartridgeDoorClosed", "CartridgePercentageLevel".
# REST API prefix for these is expected to be "DishCavity_" (unconfirmed).
ATTR_CYCLE_COUNT = "XCat_OdometerStatusCycleCount"              # unconfirmed

# Auto-dosing detergent cartridge (Whirlpool EMEA pod system), NOT rinse-aid.
# DishAttributeName keys: CartridgeLowLevel / CartridgeEmptyLevel / …
ATTR_CARTRIDGE_LOW = "DishCavity_OpStatusCartridgeLowLevel"     # unconfirmed
ATTR_CARTRIDGE_EMPTY = "DishCavity_OpStatusCartridgeEmptyLevel" # unconfirmed
ATTR_CARTRIDGE_INSERTED = "DishCavity_OpStatusCartridgeInserted" # unconfirmed
ATTR_CARTRIDGE_PERCENTAGE = "DishCavity_OpStatusCartridgePercentageLevel"  # unconfirmed

ATTR_DELAY_START = "DishCavity_DelayStatusDelayTime"            # unconfirmed
ATTR_SET_DELAY_START = "DishCavity_DelaySetDelayTime"           # unconfirmed
ATTR_CYCLE_SELECT = "DishCavity_CycleSetCycleSelect"            # unconfirmed

# ── System-level ─────────────────────────────────────────────────────────────
ATTR_CONTROL_LOCK = "Sys_OperationSetControlLock"               # unconfirmed
ATTR_QUIET_MODE = "Sys_OperationSetQuietModeEnabled"            # unconfirmed

# ── Machine state values ─────────────────────────────────────────────────────
ATTRVAL_MACHINE_STATE_STANDBY = "0"
ATTRVAL_MACHINE_STATE_SETTING = "1"
ATTRVAL_MACHINE_STATE_DELAY_COUNTDOWN = "2"
ATTRVAL_MACHINE_STATE_PAUSE = "6"
ATTRVAL_MACHINE_STATE_RUNNING = "7"
ATTRVAL_MACHINE_STATE_RUNNING_POST_CYCLE = "8"
ATTRVAL_MACHINE_STATE_COMPLETE = "10"
ATTRVAL_MACHINE_STATE_ERROR = "17"


class MachineState(Enum):
    Standby = 0
    Setting = 1
    DelayCountdown = 2
    Pause = 6
    Running = 7
    RunningPostCycle = 8
    Complete = 10
    Error = 17


MACHINE_STATE_MAP = {
    ATTRVAL_MACHINE_STATE_STANDBY: MachineState.Standby,
    ATTRVAL_MACHINE_STATE_SETTING: MachineState.Setting,
    ATTRVAL_MACHINE_STATE_DELAY_COUNTDOWN: MachineState.DelayCountdown,
    ATTRVAL_MACHINE_STATE_PAUSE: MachineState.Pause,
    ATTRVAL_MACHINE_STATE_RUNNING: MachineState.Running,
    ATTRVAL_MACHINE_STATE_RUNNING_POST_CYCLE: MachineState.RunningPostCycle,
    ATTRVAL_MACHINE_STATE_COMPLETE: MachineState.Complete,
    ATTRVAL_MACHINE_STATE_ERROR: MachineState.Error,
}


class Dishwasher(Appliance):
    """Whirlpool connected dishwasher.

    All attribute keys are UNCONFIRMED – validate against a real device.
    See module docstring for investigation notes.
    """

    def get_machine_state(self) -> MachineState | None:
        """Return current machine state."""
        raw = self._get_attribute(ATTR_MACHINE_STATE)
        if raw is None:
            return None
        state = MACHINE_STATE_MAP.get(raw)
        if state is None:
            LOGGER.warning("Unknown dishwasher machine state: %s", raw)
        return state

    def get_door_open(self) -> bool | None:
        """Return True if the door is open."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_DOOR_OPEN))

    def get_time_remaining(self) -> int | None:
        """Return estimated time remaining in seconds."""
        return self._get_int_attribute(ATTR_TIME_REMAINING)

    def get_cycle_count(self) -> int | None:
        """Return lifetime cycle count."""
        return self._get_int_attribute(ATTR_CYCLE_COUNT)

    def get_cartridge_low(self) -> bool | None:
        """Return True if the auto-dosing detergent cartridge level is low."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_CARTRIDGE_LOW))

    def get_cartridge_empty(self) -> bool | None:
        """Return True if the auto-dosing detergent cartridge is empty."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_CARTRIDGE_EMPTY))

    def get_cartridge_inserted(self) -> bool | None:
        """Return True if the auto-dosing detergent cartridge is inserted."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_CARTRIDGE_INSERTED))

    def get_cartridge_percentage(self) -> int | None:
        """Return remaining detergent cartridge level in percent (0-100)."""
        return self._get_int_attribute(ATTR_CARTRIDGE_PERCENTAGE)

    def get_delay_start(self) -> int | None:
        """Return configured delay start in hours (0 = no delay)."""
        return self._get_int_attribute(ATTR_DELAY_START)

    async def set_delay_start(self, hours: int) -> bool:
        """Set the delay start timer in hours."""
        return await self.send_attributes({ATTR_SET_DELAY_START: str(hours)})

    def get_control_locked(self) -> bool | None:
        """Return True if the control panel is locked."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_CONTROL_LOCK))

    async def set_control_locked(self, on: bool) -> bool:
        """Lock or unlock the control panel."""
        return await self.send_attributes(
            {ATTR_CONTROL_LOCK: self.bool_to_attr_value(on)}
        )

    def get_quiet_mode(self) -> bool | None:
        """Return True if quiet mode is enabled."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_QUIET_MODE))

    async def set_quiet_mode(self, on: bool) -> bool:
        """Enable or disable quiet mode."""
        return await self.send_attributes(
            {ATTR_QUIET_MODE: self.bool_to_attr_value(on)}
        )
