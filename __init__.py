"""Behringer XR18 Mixer integration for HomeAssistant."""
import logging
from .xr18 import XR18Mixer
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant import config_entries
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import STATE_ON

DOMAIN = "behringer_xr18"
CONF_XR18_SWITCH = "xr18_switch_entity_id"

# import logging

PLATFORMS = ["switch", "number"]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    ip_address = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    xr18_mixer = XR18Mixer(hass, ip_address, port)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = xr18_mixer

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    def handle_helper_state_change(event):
        new_state = event.data.get("new_state")
        _LOGGER.debug(f'new helper state {new_state}')
        if new_state:
            state = new_state.state == STATE_ON
            xr18_mixer.set_helper_state(state)

    hass.data[DOMAIN]['change_event_handler'] = async_track_state_change_event(
        hass,
        [entry.data[CONF_XR18_SWITCH]],
        handle_helper_state_change
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    mixer = hass.data[DOMAIN][entry.entry_id]
    mixer.set_helper_state(False)
    hass.data[DOMAIN].pop(entry.entry_id)
    if 'change_event_handler' in hass.data[DOMAIN]:
        hass.data[DOMAIN]['change_event_handler']()
        hass.data[DOMAIN].pop('change_event_handler')

    return True
