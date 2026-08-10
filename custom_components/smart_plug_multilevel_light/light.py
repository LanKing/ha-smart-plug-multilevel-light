from __future__ import annotations

import asyncio
from collections import Counter
from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_state_report_event,
)

from .const import (
    CONF_MODES,
    CONF_OUTLET,
    CONF_POWER_CYCLE_DELAY,
    CONF_POWER_HISTORY_SAMPLES,
    CONF_POWER_SENSOR,
    CONF_ROUND_BRIGHTNESS_TO_5,
    DOMAIN,
    MODE_BRIGHTNESS,
    MODE_NAME,
    MODE_POWER,
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
        self._power_history: list[float] = []

    @property
    def _cfg(self) -> dict[str, Any]:
        return {**self._entry.data, **self._entry.options}

    @property
    def _outlet(self) -> str:
        return str(self._cfg[CONF_OUTLET])

    @property
    def _power_sensor(self) -> str:
        return str(self._cfg[CONF_POWER_SENSOR])

    @property
    def _history_size(self) -> int:
        try:
            value = int(self._cfg.get(CONF_POWER_HISTORY_SAMPLES, 5))
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

    def _record_power(self, value: float) -> None:
        if value <= 0:
            self._power_history.clear()
            return
        self._power_history.append(float(value))
        self._power_history = self._power_history[-self._history_size :]

    @property
    def icon(self) -> str:
        return "mdi:lightbulb-multiple" if self.is_on else "mdi:lightbulb-multiple-off"

    @property
    def is_on(self) -> bool:
        outlet_state = self.hass.states.get(self._outlet)
        if outlet_state is None or outlet_state.state != "on":
            return False
        return self._float_state(self._power_sensor) > 0

    @staticmethod
    def _estimated_brightness(
        power: float,
        max_power: float,
        round_to_5: bool,
    ) -> int:
        """Estimate visual brightness from power draw."""
        if max_power <= 0:
            return 100

        ratio = max(0.0, min(1.0, power / max_power))
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

        modes = sorted(raw_modes, key=lambda mode: float(mode[MODE_POWER]))
        max_power = float(modes[-1][MODE_POWER])
        round_to_5 = bool(self._cfg.get(CONF_ROUND_BRIGHTNESS_TO_5, True))
        return [
            {
                **mode,
                MODE_BRIGHTNESS: self._estimated_brightness(
                    float(mode[MODE_POWER]), max_power, round_to_5
                ),
            }
            for mode in modes
        ]

    @staticmethod
    def _mode_index_for_power(
        power: float,
        modes: list[dict[str, Any]],
    ) -> int | None:
        if power <= 0 or not modes:
            return None

        selected = 0
        for index, mode in enumerate(modes):
            if power < float(mode[MODE_POWER]):
                break
            selected = index
        return selected

    def _history_mode_indices(self, modes: list[dict[str, Any]]) -> list[int]:
        return [
            index
            for value in self._power_history
            if (index := self._mode_index_for_power(value, modes)) is not None
        ]

    def _selected_mode_index(self, modes: list[dict[str, Any]]) -> int | None:
        """Return the most frequent threshold-mapped mode in the recent window."""
        indices = self._history_mode_indices(modes)
        if not indices:
            return None

        counts = Counter(indices)
        highest_count = max(counts.values())
        winners = {index for index, count in counts.items() if count == highest_count}

        # On a tie prefer the mode produced by the most recent reading.
        for index in reversed(indices):
            if index in winners:
                return index
        return None

    def _mode(self) -> dict[str, Any] | None:
        if not self.is_on:
            return None
        modes = self._modes_with_brightness()
        index = self._selected_mode_index(modes)
        return modes[index] if index is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        mode = self._mode()
        modes = self._modes_with_brightness()
        indices = self._history_mode_indices(modes)
        return {
            "mode": mode[MODE_NAME] if mode else "Off",
            "brightness_pct": int(mode[MODE_BRIGHTNESS]) if mode else 0,
            "measured_power": self._float_state(self._power_sensor),
            "power_history": list(self._power_history),
            "power_history_modes": [modes[index][MODE_NAME] for index in indices],
            "power_history_samples": self._history_size,
            "selected_power_mode": mode[MODE_NAME] if mode else None,
            "configured_modes": [
                {
                    "name": item[MODE_NAME],
                    "power": float(item[MODE_POWER]),
                    "brightness_pct": int(item[MODE_BRIGHTNESS]),
                }
                for item in modes
            ],
        }

    @property
    def available(self) -> bool:
        for entity_id in (self._outlet, self._power_sensor):
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
        power = self._float_state(self._power_sensor)
        outlet_state = self.hass.states.get(self._outlet)
        if outlet_state is not None and outlet_state.state == "on" and power > 0:
            self._record_power(power)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._outlet, self._power_sensor],
                self._handle_source_change,
            )
        )
        self.async_on_remove(
            async_track_state_report_event(
                self.hass,
                self._power_sensor,
                self._handle_power_report,
            )
        )

    async def _handle_source_change(self, event: Event) -> None:
        entity_id = event.data.get("entity_id")
        if entity_id == self._power_sensor:
            self._record_power(self._float_state(self._power_sensor))
        elif entity_id == self._outlet:
            outlet_state = self.hass.states.get(self._outlet)
            if outlet_state is None or outlet_state.state != "on":
                self._power_history.clear()
            else:
                self._record_power(self._float_state(self._power_sensor))
        self.async_write_ha_state()

    async def _handle_power_report(self, event: Event) -> None:
        """Record repeated writes of an unchanged power sensor state."""
        self._record_power(self._float_state(self._power_sensor))
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
