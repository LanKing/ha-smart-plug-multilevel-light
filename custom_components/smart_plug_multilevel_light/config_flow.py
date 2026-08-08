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
    CONF_CURRENT_SENSOR,
    CONF_MODES,
    CONF_OFF_CURRENT_THRESHOLD,
    CONF_OUTLET,
    CONF_POWER_CYCLE_DELAY,
    DOMAIN,
    MODE_CURRENT,
    MODE_NAME,
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


def _current_entities(hass, outlet: str) -> list[str]:
    siblings = _sibling_entities(hass, outlet)
    return [
        entity_id
        for entity_id in siblings
        if entity_id.startswith("sensor.")
        and _device_class(hass, entity_id) == "current"
    ]


def _candidate_outlets(hass) -> list[str]:
    """Return primary switches whose device also exposes a current sensor."""
    registry = er.async_get(hass)
    result: list[str] = []

    for item in registry.entities.values():
        if not item.entity_id.startswith("switch.") or item.disabled:
            continue
        if item.entity_category is not None:
            continue
        if _current_entities(hass, item.entity_id):
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
    """Return a native object selector.

    The bundled frontend module enhances its Add/Edit dialogs with live measured
    current while Home Assistant's native object selector remains the fallback.
    """
    return selector.selector(
        {
            "object": {
                "multiple": True,
                "label_field": MODE_NAME,
                "description_field": MODE_CURRENT,
                "fields": {
                    MODE_NAME: {
                        "label": "Mode name",
                        "required": True,
                        "selector": {"text": {}},
                    },
                    MODE_CURRENT: {
                        "label": "Current threshold",
                        "required": True,
                        "selector": {
                            "number": {
                                "min": 0,
                                "max": 100,
                                "step": 0.001,
                                "unit_of_measurement": "A",
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
    current_entities: list[str],
    defaults: dict[str, Any] | None = None,
) -> vol.Schema:
    defaults = defaults or {}

    kwargs: dict[str, Any] = {"domain": "sensor"}
    if current_entities:
        kwargs["include_entities"] = current_entities

    configured_current = defaults.get(CONF_CURRENT_SENSOR)
    if not configured_current and current_entities:
        configured_current = current_entities[0]

    current_key = (
        vol.Required(CONF_CURRENT_SENSOR, default=configured_current)
        if configured_current
        else vol.Required(CONF_CURRENT_SENSOR)
    )

    modes_default = defaults.get(CONF_MODES, [])

    return vol.Schema(
        {
            vol.Required(
                "name", default=defaults.get("name", "Light")
            ): selector.TextSelector(),
            current_key: selector.selector({"entity": kwargs}),
            vol.Required(
                CONF_OFF_CURRENT_THRESHOLD,
                default=defaults.get(CONF_OFF_CURRENT_THRESHOLD, 0.005),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=100,
                    step=0.001,
                    unit_of_measurement="A",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
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
            vol.Required(CONF_MODES, default=modes_default): _modes_selector(),
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
            current = float(row[MODE_CURRENT])
        except (KeyError, TypeError, ValueError):
            continue
        result.append({MODE_NAME: name, MODE_CURRENT: current})

    return sorted(result, key=lambda mode: mode[MODE_CURRENT])


class SmartPlugMultiLevelLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Plug Multi-Level Light."""

    VERSION = 3

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
        currents = _current_entities(self.hass, self._outlet)

        if not currents:
            return self.async_abort(reason="current_sensor_missing")

        defaults: dict[str, Any] = {
            CONF_CURRENT_SENSOR: currents[0],
            CONF_OFF_CURRENT_THRESHOLD: 0.005,
            CONF_POWER_CYCLE_DELAY: 0.7,
            CONF_MODES: [],
        }

        if user_input is not None:
            modes = _normalize_modes(user_input.get(CONF_MODES))
            errors: dict[str, str] = {}
            if not modes:
                errors[CONF_MODES] = "at_least_one_mode"
            if errors:
                defaults.update(user_input)
                return self.async_show_form(
                    step_id="settings",
                    data_schema=_settings_schema(
                        current_entities=currents,
                        defaults=defaults,
                    ),
                    errors=errors,
                )

            title = str(user_input.pop("name"))
            data = {
                CONF_OUTLET: self._outlet,
                **user_input,
                CONF_MODES: modes,
            }
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="settings",
            data_schema=_settings_schema(
                current_entities=currents,
                defaults=defaults,
            ),
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
        currents = _current_entities(self.hass, outlet)

        configured_current = current.get(CONF_CURRENT_SENSOR)
        if configured_current and configured_current not in currents:
            currents.append(configured_current)

        defaults = {
            "name": self.config_entry.title,
            CONF_CURRENT_SENSOR: configured_current or (currents[0] if currents else None),
            CONF_OFF_CURRENT_THRESHOLD: current.get(
                CONF_OFF_CURRENT_THRESHOLD, 0.005
            ),
            CONF_POWER_CYCLE_DELAY: current.get(CONF_POWER_CYCLE_DELAY, 0.7),
            CONF_MODES: current.get(CONF_MODES, []),
        }

        if user_input is not None:
            modes = _normalize_modes(user_input.get(CONF_MODES))
            if not modes:
                defaults.update(user_input)
                return self.async_show_form(
                    step_id="init",
                    data_schema=_settings_schema(
                        current_entities=currents,
                        defaults=defaults,
                    ),
                    errors={CONF_MODES: "at_least_one_mode"},
                )

            title = str(user_input.pop("name"))
            self.hass.config_entries.async_update_entry(
                self.config_entry, title=title
            )
            return self.async_create_entry(
                data={**user_input, CONF_MODES: modes}
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_settings_schema(
                current_entities=currents,
                defaults=defaults,
            ),
        )
