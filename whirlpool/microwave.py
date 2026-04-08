"""Whirlpool built-in microwave oven (MWO / combo) appliance.

Attribute prefixes confirmed from APK assets (TSCookingDefinitions.json):
  - MwoCavity_ prefix for cavity-specific attributes
  - Sys_Operation* / Sys_Display* for system-level attributes

Covers DDM model keys:
  DDM_COOKING_BI_MWO_*       – built-in microwave oven combo
  DDM_COOKING_BIMWO_*        – speed/combi oven with microwave
  DDM_COOKING_BIO_MWO_*      – built-in oven with microwave feature
"""

import logging
from enum import Enum

from .appliance import Appliance

LOGGER = logging.getLogger(__name__)

# ── Cavity-level read attributes ────────────────────────────────────────────
ATTR_DOOR_OPEN = "MwoCavity_OpStatusDoorOpen"
ATTR_LIGHT = "MwoCavity_DisplaySetLightOn"
ATTR_STATE = "MwoCavity_OpStatusState"
ATTR_COOK_MODE = "MwoCavity_CycleSetCommonMode"
ATTR_TARGET_TEMP = "MwoCavity_CycleSetTargetTemp"
ATTR_CURRENT_TEMP = "MwoCavity_DisplStatusDisplayTemp"
ATTR_COOK_TIME_ELAPSED = "MwoCavity_TimeStatusCycleTimeElapsed"
ATTR_SET_OPERATION = "MwoCavity_OpSetOperations"

# ── System-level attributes (shared with oven) ───────────────────────────────
ATTR_CONTROL_LOCK = "Sys_OperationSetControlLock"
ATTR_QUIET_MODE = "Sys_OperationSetQuietModeEnabled"
ATTR_DISPLAY_BRIGHTNESS = "Sys_DisplaySetBrightnessPercent"

# ── Cavity state values ───────────────────────────────────────────────────────
ATTRVAL_STATE_STANDBY = "0"
ATTRVAL_STATE_PREHEATING = "1"
ATTRVAL_STATE_COOKING = "2"
ATTRVAL_STATE_NOT_PRESENT = "4"

# ── Cook mode values (subset that applies to MWO cavity) ─────────────────────
ATTRVAL_COOK_MODE_STANDBY = "0"
ATTRVAL_COOK_MODE_MICROWAVE = "14"      # pure microwave mode
ATTRVAL_COOK_MODE_GRILL = "15"          # grill / broil
ATTRVAL_COOK_MODE_COMBI_MW_GRILL = "16" # microwave + grill
ATTRVAL_COOK_MODE_FORCED_AIR = "3"      # convection fan only
ATTRVAL_COOK_MODE_COMBI_MW_FA = "18"    # microwave + forced air

# ── Operation values ──────────────────────────────────────────────────────────
ATTRVAL_OPERATION_CANCEL = "1"
ATTRVAL_OPERATION_START = "2"
ATTRVAL_OPERATION_MODIFY = "4"
ATTRVAL_OPERATION_PAUSE = "5"


class CavityState(Enum):
    Standby = 0
    Preheating = 1
    Cooking = 2
    NotPresent = 4


CAVITY_STATE_MAP = {
    ATTRVAL_STATE_STANDBY: CavityState.Standby,
    ATTRVAL_STATE_PREHEATING: CavityState.Preheating,
    ATTRVAL_STATE_COOKING: CavityState.Cooking,
    ATTRVAL_STATE_NOT_PRESENT: CavityState.NotPresent,
}


class CookMode(Enum):
    Standby = 0
    Microwave = 14
    Grill = 15
    CombiMicrowaveGrill = 16
    ForcedAir = 3
    CombiMicrowaveForcedAir = 18


COOK_MODE_MAP = {
    ATTRVAL_COOK_MODE_STANDBY: CookMode.Standby,
    ATTRVAL_COOK_MODE_MICROWAVE: CookMode.Microwave,
    ATTRVAL_COOK_MODE_GRILL: CookMode.Grill,
    ATTRVAL_COOK_MODE_COMBI_MW_GRILL: CookMode.CombiMicrowaveGrill,
    ATTRVAL_COOK_MODE_FORCED_AIR: CookMode.ForcedAir,
    ATTRVAL_COOK_MODE_COMBI_MW_FA: CookMode.CombiMicrowaveForcedAir,
}

COOK_MODE_SET_MAP = {v: k for k, v in COOK_MODE_MAP.items()}


class CookOperation(Enum):
    Cancel = 1
    Start = 2
    Modify = 4
    Pause = 5


COOK_OPERATION_MAP = {
    CookOperation.Cancel: ATTRVAL_OPERATION_CANCEL,
    CookOperation.Start: ATTRVAL_OPERATION_START,
    CookOperation.Modify: ATTRVAL_OPERATION_MODIFY,
    CookOperation.Pause: ATTRVAL_OPERATION_PAUSE,
}


class Microwave(Appliance):
    """Whirlpool built-in microwave oven (MwoCavity_ prefix)."""

    # ── State ────────────────────────────────────────────────────────────────

    def get_cavity_state(self) -> CavityState | None:
        """Return current cavity state."""
        raw = self._get_attribute(ATTR_STATE)
        if raw is None:
            return None
        state = CAVITY_STATE_MAP.get(raw)
        if state is None:
            LOGGER.warning("Unknown MWO cavity state: %s", raw)
        return state

    def get_door_open(self) -> bool | None:
        """Return True if the door is open."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_DOOR_OPEN))

    # ── Temperature ──────────────────────────────────────────────────────────

    def get_temp(self) -> float | None:
        """Return current cavity temperature (°C)."""
        raw = self._get_int_attribute(ATTR_CURRENT_TEMP)
        if raw is None or raw == 0:
            return None
        return raw / 10

    def get_target_temp(self) -> float | None:
        """Return target cavity temperature (°C)."""
        raw = self._get_int_attribute(ATTR_TARGET_TEMP)
        if raw is None or raw == 0:
            return None
        return raw / 10

    # ── Cook time ────────────────────────────────────────────────────────────

    def get_cook_time_elapsed(self) -> int | None:
        """Return elapsed cook time in seconds."""
        return self._get_int_attribute(ATTR_COOK_TIME_ELAPSED)

    # ── Cook mode ────────────────────────────────────────────────────────────

    def get_cook_mode(self) -> CookMode | None:
        """Return current cook mode."""
        raw = self._get_attribute(ATTR_COOK_MODE)
        if raw is None:
            return None
        mode = COOK_MODE_MAP.get(raw)
        if mode is None:
            LOGGER.warning("Unknown MWO cook mode: %s", raw)
        return mode

    # ── Light ────────────────────────────────────────────────────────────────

    def get_light(self) -> bool | None:
        """Return True if the cavity light is on."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_LIGHT))

    async def set_light(self, on: bool) -> bool:
        """Turn the cavity light on or off."""
        return await self.send_attributes({ATTR_LIGHT: self.bool_to_attr_value(on)})

    # ── Control lock ─────────────────────────────────────────────────────────

    def get_control_locked(self) -> bool | None:
        """Return True if the control panel is locked."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_CONTROL_LOCK))

    async def set_control_locked(self, on: bool) -> bool:
        """Lock or unlock the control panel."""
        return await self.send_attributes(
            {ATTR_CONTROL_LOCK: self.bool_to_attr_value(on)}
        )

    # ── Quiet mode ───────────────────────────────────────────────────────────

    def get_quiet_mode(self) -> bool | None:
        """Return True if quiet mode is enabled."""
        return self.attr_value_to_bool(self._get_attribute(ATTR_QUIET_MODE))

    async def set_quiet_mode(self, on: bool) -> bool:
        """Enable or disable quiet mode."""
        return await self.send_attributes(
            {ATTR_QUIET_MODE: self.bool_to_attr_value(on)}
        )

    # ── Cook control ─────────────────────────────────────────────────────────

    async def set_cook(
        self,
        target_temp: float,
        mode: CookMode = CookMode.Microwave,
        operation: CookOperation = CookOperation.Start,
    ) -> bool:
        """Start / modify a cooking operation."""
        return await self.send_attributes(
            {
                ATTR_COOK_MODE: COOK_MODE_SET_MAP[mode],
                ATTR_TARGET_TEMP: str(round(target_temp * 10)),
                ATTR_SET_OPERATION: COOK_OPERATION_MAP[operation],
            }
        )

    async def stop_cook(self) -> bool:
        """Cancel the current cooking operation."""
        return await self.send_attributes(
            {ATTR_SET_OPERATION: COOK_OPERATION_MAP[CookOperation.Cancel]}
        )
