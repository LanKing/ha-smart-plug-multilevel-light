from __future__ import annotations

import asyncio
from collections import Counter
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    CONF_CURRENT_HISTORY_SAMPLES,
    CONF_CURRENT_SENSOR,
    CONF_MODES,
    CONF_OUTLET,
    CONF_POWER_CYCLE_DELAY,
    CONF_ROUND_BRIGHTNESS_TO_5,
    DOMAIN,
    MODE_BRIGHTNESS,
    MODE_CURRENT,
    MODE_NAME,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([SmartPlugMultiLevelLight(hass, entry)])


class SmartPlugMultiLevelLight(LightEntity):
    """A virtual multi-level light backed by a metering smart plug."""

    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_color_mode = ColorMode.ONOFF
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_name = entry.title
        self._attr_unique_id = entry.entry_id
        self._current_history: list[float] = []

    @property
    def _cfg(self) -> dict[str, Any]:
        return {**self._entry.data, **self._entry.options}

    @property
    def _outlet(self) -> str:
        return str(self._cfg[CONF_OUTLET])

    @property
    def _current_sensor(self) -> str:
        return str(self._cfg[CONF_CURRENT_SENSOR])

    @property
    def _history_size(self) -> int:
        try:
            value = int(self._cfg.get(CONF_CURRENT_HISTORY_SAMPLES, 5))
        except (TypeError, ValueError):
            value = 5
        return max(1, min(100, value))

    def _float_state(self, entity_id: str) -> float:
        state = self.hass.states.get(entity_id)
        if state is None:
            return 0.0
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _normalized_current(value: float) -> float:
        """Normalize current to the 0.001 A resolution used by configuration."""
        return round(float(value), 3)

    def _record_current(self, value: float) -> None:
        value = self._normalized_current(value)
        if value <= 0:
            self._current_history.clear()
            return
        self._current_history.append(value)
        self._current_history = self._current_history[-self._history_size :]

    @property
    def icon(self) -> str:
        return "mdi:lightbulb-multiple" if self.is_on else "mdi:lightbulb-multiple-off"

    @property
    def is_on(self) -> bool:
        outlet_state = self.hass.states.get(self._outlet)
        if outlet_state is None or outlet_state.state != "on":
            return False
        return self._float_state(self._current_sensor) > 0

    @staticmethod
    def _estimated_brightness(
        current: float,
        max_current: float,
        round_to_5: bool,
    ) -> int:
        """Estimate visual brightness from current draw."""
        if max_current <= 0:
            return 100

        ratio = max(0.0, min(1.0, current / max_current))
        estimated = ratio**3 * 100

        if round_to_5:
            rounded = 5 * int(estimated / 5 + 0.5)
            return max(5, min(100, rounded))

        rounded = int(estimated + 0.5)
        return max(1, min(100, rounded))

    def _modes_with_brightness(self) -> list[dict[str, Any]]:
        raw_modes = self._cfg.get(CONF_MODES, [])
        if not raw_modes:
            return []

        modes = sorted(raw_modes, key=lambda mode: float(mode[MODE_CURRENT]))
        max_current = float(modes[-1][MODE_CURRENT])
        round_to_5 = bool(self._cfg.get(CONF_ROUND_BRIGHTNESS_TO_5, True))
        return [
            {
                **mode,
                MODE_BRIGHTNESS: self._estimated_brightness(
                    float(mode[MODE_CURRENT]), max_current, round_to_5
                ),
            }
            for mode in modes
        ]

    def _selected_current(self) -> float | None:
        """Return the most frequent configured current in the recent sample window."""
        configured = {
            self._normalized_current(float(mode[MODE_CURRENT]))
            for mode in self._cfg.get(CONF_MODES, [])
        }
        if not configured:
            return None

        valid = [value for value in self._current_history if value in configured]
        if not valid:
            return None

        counts = Counter(valid)
        highest_count = max(counts.values())
        winners = {value for value, count in counts.items() if count == highest_count}

        # On a tie prefer the value seen most recently in the window.
        for value in reversed(valid):
            if value in winners:
                return value
        return None

    def _mode(self) -> dict[str, Any] | None:
        if not self.is_on:
            return None
        selected_current = self._selected_current()
        if selected_current is None:
            return None

        for mode in self._modes_with_brightness():
            if self._normalized_current(float(mode[MODE_CURRENT])) == selected_current:
                return mode
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        mode = self._mode()
        modes = self._modes_with_brightness()
        configured = {
            self._normalized_current(float(item[MODE_CURRENT])) for item in modes
        }
        valid_history = [value for value in self._current_history if value in configured]
        return {
            "mode": mode[MODE_NAME] if mode else "Off",
            "brightness_pct": int(mode[MODE_BRIGHTNESS]) if mode else 0,
            "measured_current": self._float_state(self._current_sensor),
            "current_history": list(self._current_history),
            "valid_current_history": valid_history,
            "current_history_samples": self._history_size,
            "selected_current": self._selected_current(),
            "configured_modes": [
                {
                    "name": item[MODE_NAME],
                    "current": float(item[MODE_CURRENT]),
                    "brightness_pct": int(item[MODE_BRIGHTNESS]),
                }
                for item in modes
            ],
        }

    @property
    def available(self) -> bool:
        for entity_id in (self._outlet, self._current_sensor):
            state = self.hass.states.get(entity_id)
            if state is None or state.state in {"unknown", "unavailable"}:
                return False
        return True

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="Smart Plug Multi-Level Light",
            model="Multi-level light via metered smart plug",
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        current = self._float_state(self._current_sensor)
        outlet_state = self.hass.states.get(self._outlet)
        if outlet_state is not None and outlet_state.state == "on" and current > 0:
            self._record_current(current)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._outlet, self._current_sensor],
                self._handle_source_change,
            )
        )

    async def _handle_source_change(self, event: Event) -> None:
        entity_id = event.data.get("entity_id")
        if entity_id == self._current_sensor:
            self._record_current(self._float_state(self._current_sensor))
        elif entity_id == self._outlet:
            outlet_state = self.hass.states.get(self._outlet)
            if outlet_state is None or outlet_state.state != "on":
                self._current_history.clear()
            else:
                self._record_current(self._float_state(self._current_sensor))
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        outlet_state = self.hass.states.get(self._outlet)
        if outlet_state is None:
            return

        if outlet_state.state == "off":
            await self.hass.services.async_call(
                "switch", "turn_on", {"entity_id": self._outlet}, blocking=True
            )
            return

        if not self.is_on:
            await self.hass.services.async_call(
                "switch", "turn_off", {"entity_id": self._outlet}, blocking=True
            )
            await asyncio.sleep(float(self._cfg.get(CONF_POWER_CYCLE_DELAY, 0.7)))
            await self.hass.services.async_call(
                "switch", "turn_on", {"entity_id": self._outlet}, blocking=True
            )

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.hass.services.async_call(
            "switch", "turn_off", {"entity_id": self._outlet}, blocking=True
        )
