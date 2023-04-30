"""Behringer XR18 Mixer integration for HomeAssistant."""
from .xr18 import XR18Mixer
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant import config_entries

import logging

DOMAIN = "behringer_xr18"
PLATFORMS = ["sensor", "binary_sensor"]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    ip_address = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    xr18_mixer = XR18Mixer(ip_address, port)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = xr18_mixer

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id)

    return True
