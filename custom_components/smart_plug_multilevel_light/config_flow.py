from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow
from homeassistant.const import ATTR_DEVICE_CLASS
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er, selector

from . import async_ensure_frontend_assets
from .const import (
    CONF_MODES,
    CONF_OUTLET,
    CONF_POWER_CYCLE_DELAY,
    CONF_POWER_HISTORY_SAMPLES,
    CONF_POWER_SENSOR,
    CONF_ROUND_BRIGHTNESS_TO_5,
    DOMAIN,
    MODE_NAME,
    MODE_POWER,
)


def _device_class(hass, entity_id: str) -> str | None:
    state = hass.states.get(entity_id)
    if state is None:
        return None
    value = state.attributes.get(ATTR_DEVICE_CLASS)
    return str(value) if value is not None else None


def _device_id_for_entity(hass, entity_id: str) -> str | None:
    registry = er.async_get(hass)
    entry = registry.async_get(entity_id)
    return entry.device_id if entry else None


def _sibling_entities(hass, entity_id: str) -> list[str]:
    """Return enabled entities belonging to the same HA device as entity_id."""
    device_id = _device_id_for_entity(hass, entity_id)
    if not device_id:
        return []

    registry = er.async_get(hass)
    return [
        item.entity_id
        for item in er.async_entries_for_device(
            registry, device_id, include_disabled_entities=False
        )
    ]


def _power_entities(hass, outlet: str) -> list[str]:
    siblings = _sibling_entities(hass, outlet)
    return [
        entity_id
        for entity_id in siblings
        if entity_id.startswith("sensor.")
        and _device_class(hass, entity_id) == "power"
    ]


def _candidate_outlets(hass) -> list[str]:
    """Return primary switches whose device also exposes a power sensor."""
    registry = er.async_get(hass)
    result: list[str] = []

    for item in registry.entities.values():
        if not item.entity_id.startswith("switch.") or item.disabled:
            continue
        if item.entity_category is not None:
            continue
        if _power_entities(hass, item.entity_id):
            result.append(item.entity_id)

    return sorted(result)


def _outlet_schema(hass, default: str | None = None) -> vol.Schema:
    candidates = _candidate_outlets(hass)
    entity_cfg: dict[str, Any] = {"domain": "switch"}
    if candidates:
        entity_cfg["include_entities"] = candidates

    key = vol.Required(CONF_OUTLET)
    if default:
        key = vol.Required(CONF_OUTLET, default=default)

    return vol.Schema({key: selector.selector({"entity": entity_cfg})})


def _modes_selector():
    """Return a native object selector enhanced by the bundled frontend UI."""
    return selector.selector(
        {
            "object": {
                "multiple": True,
                "label_field": MODE_NAME,
                "description_field": MODE_POWER,
                "fields": {
                    MODE_NAME: {
                        "label": "Mode name",
                        "required": True,
                        "selector": {"text": {}},
                    },
                    MODE_POWER: {
                        "label": "Power value",
                        "required": True,
                        "selector": {
                            "number": {
                                "min": 0,
                                "max": 10000,
                                "step": 0.1,
                                "unit_of_measurement": "W",
                                "mode": "box",
                            }
                        },
                    },
                },
            }
        }
    )


def _settings_schema(
    *,
    power_entities: list[str],
    defaults: dict[str, Any] | None = None,
) -> vol.Schema:
    defaults = defaults or {}

    kwargs: dict[str, Any] = {"domain": "sensor"}
    if power_entities:
        kwargs["include_entities"] = power_entities

    configured_power = defaults.get(CONF_POWER_SENSOR)
    if not configured_power and power_entities:
        configured_power = power_entities[0]

    power_key = (
        vol.Required(CONF_POWER_SENSOR, default=configured_power)
        if configured_power
        else vol.Required(CONF_POWER_SENSOR)
    )

    return vol.Schema(
        {
            vol.Required(
                "name", default=defaults.get("name", "Light")
            ): selector.TextSelector(),
            power_key: selector.selector({"entity": kwargs}),
            vol.Required(
                CONF_POWER_CYCLE_DELAY,
                default=defaults.get(CONF_POWER_CYCLE_DELAY, 0.7),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=10,
                    step=0.1,
                    unit_of_measurement="s",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_POWER_HISTORY_SAMPLES,
                default=defaults.get(CONF_POWER_HISTORY_SAMPLES, 5),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=100,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_ROUND_BRIGHTNESS_TO_5,
                default=defaults.get(CONF_ROUND_BRIGHTNESS_TO_5, False),
            ): selector.BooleanSelector(),
            vol.Required(CONF_MODES, default=defaults.get(CONF_MODES, [])): _modes_selector(),
        }
    )


def _normalize_modes(raw_modes: Any) -> list[dict[str, Any]]:
    """Validate and normalize the editable row list."""
    if not isinstance(raw_modes, list):
        return []

    result: list[dict[str, Any]] = []
    for row in raw_modes:
        if not isinstance(row, dict):
            continue
        name = str(row.get(MODE_NAME, "")).strip()
        if not name:
            continue
        try:
            power = round(float(row[MODE_POWER]), 1)
        except (KeyError, TypeError, ValueError):
            continue
        result.append({MODE_NAME: name, MODE_POWER: power})

    return sorted(result, key=lambda mode: mode[MODE_POWER])


class SmartPlugMultiLevelLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Plug Multi-Level Light."""

    VERSION = 7

    def __init__(self) -> None:
        self._outlet: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await async_ensure_frontend_assets(self.hass)

        if user_input is not None:
            self._outlet = str(user_input[CONF_OUTLET])
            return await self.async_step_settings()

        return self.async_show_form(
            step_id="user", data_schema=_outlet_schema(self.hass)
        )

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await async_ensure_frontend_assets(self.hass)
        assert self._outlet is not None
        powers = _power_entities(self.hass, self._outlet)

        if not powers:
            return self.async_abort(reason="power_sensor_missing")

        defaults: dict[str, Any] = {
            CONF_POWER_SENSOR: powers[0],
            CONF_POWER_CYCLE_DELAY: 0.7,
            CONF_POWER_HISTORY_SAMPLES: 5,
            CONF_ROUND_BRIGHTNESS_TO_5: False,
            CONF_MODES: [],
        }

        if user_input is not None:
            modes = _normalize_modes(user_input.get(CONF_MODES))
            if not modes:
                defaults.update(user_input)
                return self.async_show_form(
                    step_id="settings",
                    data_schema=_settings_schema(
                        power_entities=powers,
                        defaults=defaults,
                    ),
                    errors={CONF_MODES: "at_least_one_mode"},
                )

            title = str(user_input.pop("name"))
            return self.async_create_entry(
                title=title,
                data={CONF_OUTLET: self._outlet, **user_input, CONF_MODES: modes},
            )

        return self.async_show_form(
            step_id="settings",
            data_schema=_settings_schema(power_entities=powers, defaults=defaults),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlow:
        return SmartPlugMultiLevelLightOptionsFlow()


class SmartPlugMultiLevelLightOptionsFlow(OptionsFlow):
    """Edit all mutable settings and the complete mode table on one page."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        await async_ensure_frontend_assets(self.hass)

        current = {**self.config_entry.data, **self.config_entry.options}
        outlet = str(current[CONF_OUTLET])
        powers = _power_entities(self.hass, outlet)

        configured_power = current.get(CONF_POWER_SENSOR)
        if configured_power and configured_power not in powers:
            powers.append(configured_power)

        defaults = {
            "name": self.config_entry.title,
            CONF_POWER_SENSOR: configured_power or (powers[0] if powers else None),
            CONF_POWER_CYCLE_DELAY: current.get(CONF_POWER_CYCLE_DELAY, 0.7),
            CONF_POWER_HISTORY_SAMPLES: current.get(CONF_POWER_HISTORY_SAMPLES, 5),
            CONF_ROUND_BRIGHTNESS_TO_5: current.get(CONF_ROUND_BRIGHTNESS_TO_5, False),
            CONF_MODES: current.get(CONF_MODES, []),
        }

        if user_input is not None:
            modes = _normalize_modes(user_input.get(CONF_MODES))
            if not modes:
                defaults.update(user_input)
                return self.async_show_form(
                    step_id="init",
                    data_schema=_settings_schema(
                        power_entities=powers,
                        defaults=defaults,
                    ),
                    errors={CONF_MODES: "at_least_one_mode"},
                )

            title = str(user_input.pop("name"))
            self.hass.config_entries.async_update_entry(
                self.config_entry, title=title
            )
            return self.async_create_entry(data={**user_input, CONF_MODES: modes})

        return self.async_show_form(
            step_id="init",
            data_schema=_settings_schema(power_entities=powers, defaults=defaults),
        )
