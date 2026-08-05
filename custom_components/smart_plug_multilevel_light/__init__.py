from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS

_CARD_URL = f"/api/{DOMAIN}/smart-plug-multilevel-light-card.js"
_CARD_FILE = Path(__file__).parent / "static" / "smart-plug-multilevel-light-card.js"
_DATA_STATIC_REGISTERED = "static_registered"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Plug Multi-Level Light from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})

    if not domain_data.get(_DATA_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(_CARD_URL, str(_CARD_FILE), False)]
        )
        domain_data[_DATA_STATIC_REGISTERED] = True

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
