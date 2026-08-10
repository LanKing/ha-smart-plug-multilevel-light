from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA, MODE_STORAGE
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

_VERSION = "0.7.22"
_CARD_PATH = f"/api/{DOMAIN}/smart-plug-multilevel-light-card.js"
_CARD_URL = f"{_CARD_PATH}?v={_VERSION}"
_CARD_FILE = Path(__file__).parent / "static" / "smart-plug-multilevel-light-card.js"
_LOCALES_PATH = f"/api/{DOMAIN}/smart-plug-multilevel-light-locales.js"
_LOCALES_URL = f"{_LOCALES_PATH}?v={_VERSION}"
_LOCALES_FILE = Path(__file__).parent / "static" / "smart-plug-multilevel-light-locales.js"
_CONFIG_UI_PATH = f"/api/{DOMAIN}/smart-plug-multilevel-light-config-v2.js"
_CONFIG_UI_URL = f"{_CONFIG_UI_PATH}?v={_VERSION}"
_CONFIG_UI_FILE = Path(__file__).parent / "static" / "smart-plug-multilevel-light-config-v2.js"
_HELPER_FIX_PATH = f"/api/{DOMAIN}/smart-plug-multilevel-light-helper-fix.js"
_HELPER_FIX_URL = f"{_HELPER_FIX_PATH}?v={_VERSION}"
_HELPER_FIX_FILE = Path(__file__).parent / "static" / "smart-plug-multilevel-light-helper-fix.js"
_DATA_STATIC_REGISTERED = "static_registered"
_DATA_CONFIG_UI_REGISTERED = "config_ui_registered"
_DATA_RESOURCE_REGISTERED = "resource_registered"


async def async_ensure_frontend_assets(hass: HomeAssistant) -> None:
    """Publish frontend files and load localization/config-flow UI modules."""
    domain_data = hass.data.setdefault(DOMAIN, {})

    if not domain_data.get(_DATA_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(_CARD_PATH, str(_CARD_FILE), False),
                StaticPathConfig(_LOCALES_PATH, str(_LOCALES_FILE), False),
                StaticPathConfig(_CONFIG_UI_PATH, str(_CONFIG_UI_FILE), False),
                StaticPathConfig(_HELPER_FIX_PATH, str(_HELPER_FIX_FILE), False),
            ]
        )
        domain_data[_DATA_STATIC_REGISTERED] = True

    if domain_data.get(_DATA_CONFIG_UI_REGISTERED):
        return

    if not await async_setup_component(hass, "frontend", {}):
        _LOGGER.warning("Could not set up frontend; config-flow UI was not registered")
        return

    add_extra_js_url(hass, _LOCALES_URL)
    add_extra_js_url(hass, _CONFIG_UI_URL)
    add_extra_js_url(hass, _HELPER_FIX_URL)
    domain_data[_DATA_CONFIG_UI_REGISTERED] = True


async def _async_register_card_resource(hass: HomeAssistant) -> None:
    """Register the bundled Lovelace card as a frontend resource."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(_DATA_RESOURCE_REGISTERED):
        return

    if not await async_setup_component(hass, "lovelace", {}):
        _LOGGER.warning("Could not set up Lovelace; card resource was not registered")
        return

    lovelace_data = hass.data[LOVELACE_DATA]
    if lovelace_data.resource_mode != MODE_STORAGE:
        _LOGGER.warning(
            "Lovelace resources are managed in YAML mode; add %s manually",
            _CARD_URL,
        )
        return

    resources = lovelace_data.resources
    await resources.async_get_info()

    existing = next(
        (
            item
            for item in resources.async_items()
            if str(item.get(CONF_URL, "")).split("?", 1)[0] == _CARD_PATH
        ),
        None,
    )

    if existing is None:
        await resources.async_create_item({"res_type": "module", CONF_URL: _CARD_URL})
    elif existing.get(CONF_URL) != _CARD_URL:
        await resources.async_update_item(existing["id"], {CONF_URL: _CARD_URL})

    domain_data[_DATA_RESOURCE_REGISTERED] = True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Plug Multi-Level Light from a config entry."""
    await async_ensure_frontend_assets(hass)
    await _async_register_card_resource(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Smart Plug Multi-Level Light."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
