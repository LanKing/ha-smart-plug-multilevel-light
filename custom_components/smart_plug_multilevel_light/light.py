from __future__ import annotations

import asyncio
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
    CONF_CURRENT_SENSOR,
    CONF_CURRENT_STABILITY_SAMPLES,
    CONF_MODES,
    CONF_OFF_CURRENT_THRESHOLD,
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
        self._stable_current: float | None = None
        self._current_candidate: float | None = None
        self._current_candidate_count = 0

    @property
    def _cfg(self) -> dict[str, Any]:
        return {**self._entry.data, **self._entry.options}

    @property
    def _outlet(self) -> str:
        return str(self._cfg[CONF_OUTLET])

    @property
    def _current_sensor(self) -> str:
        return str(self._cfg[CONF_CURRENT_SENSOR])

    def _float_state(self, entity_id: str) -> float:
        state = self.hass.states.get(entity_id)
        if state is None:
            return 0.0
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return 0.0

    @property
    def _off_current_threshold(self) -> float:
        return float(self._cfg.get(CONF_OFF_CURRENT_THRESHOLD, 0.005))

    @property
    def _current_stability_samples(self) -> int:
        try:
            value = int(self._cfg.get(CONF_CURRENT_STABILITY_SAMPLES, 2))
        except (TypeError, ValueError):
            value = 2
        return max(0, min(10, value))

    def _reset_current_filter(self, accepted_current: float | None = None) -> None:
        if accepted_current is not None:
            self._stable_current = accepted_current
        self._current_candidate = None
        self._current_candidate_count = 0

    def _process_current_sample(self) -> None:
        """Accept current changes after N identical samples while keeping ON/OFF immediate."""
        current = self._float_state(self._current_sensor)
        outlet_state = self.hass.states.get(self._outlet)
        outlet_on = outlet_state is not None and outlet_state.state == "on"
        samples = self._current_stability_samples

        # OFF and transition to ON are intentionally never delayed by the filter.
        if not outlet_on or current <= self._off_current_threshold:
            self._reset_current_filter(current)
            return

        if self._stable_current is None or self._stable_current <= self._off_current_threshold:
            self._reset_current_filter(current)
            return

        # 0 disables filtering; 1 means a single sample is enough.
        if samples <= 1:
            self._reset_current_filter(current)
            return

        if current == self._stable_current:
            self._reset_current_filter()
            return

        if current == self._current_candidate:
            self._current_candidate_count += 1
        else:
            self._current_candidate = current
            self._current_candidate_count = 1

        if self._current_candidate_count >= samples:
            self._reset_current_filter(current)

    def _mode_current(self) -> float:
        if self._current_stability_samples <= 1 or self._stable_current is None:
            return self._float_state(self._current_sensor)
        return self._stable_current

    @property
    def icon(self) -> str:
        return "mdi:lightbulb-multiple" if self.is_on else "mdi:lightbulb-multiple-off"

    @property
    def is_on(self) -> bool:
        outlet_state = self.hass.states.get(self._outlet)
        if outlet_state is None or outlet_state.state != "on":
            return False
        return self._float_state(self._current_sensor) > self._off_current_threshold

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

    def _mode(self) -> dict[str, Any] | None:
        if not self.is_on:
            return None
        modes = self._modes_with_brightness()
        if not modes:
            return None
        current = self._mode_current()

        selected = modes[0]
        for mode in modes:
            if current < float(mode[MODE_CURRENT]):
                break
            selected = mode
        return selected

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        mode = self._mode()
        modes = self._modes_with_brightness()
        return {
            "mode": mode[MODE_NAME] if mode else "Off",
            "brightness_pct": int(mode[MODE_BRIGHTNESS]) if mode else 0,
            "measured_current": self._float_state(self._current_sensor),
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
        self._stable_current = self._float_state(self._current_sensor)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._outlet, self._current_sensor],
                self._handle_source_change,
            )
        )
        self.async_on_remove(
            async_track_state_report_event(
                self.hass,
                self._current_sensor,
                self._handle_current_report,
            )
        )

    async def _handle_source_change(self, event: Event) -> None:
        if event.data.get("entity_id") == self._current_sensor:
            self._process_current_sample()
        else:
            current = self._float_state(self._current_sensor)
            self._reset_current_filter(current)
        self.async_write_ha_state()

    async def _handle_current_report(self, event: Event) -> None:
        self._process_current_sample()
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
