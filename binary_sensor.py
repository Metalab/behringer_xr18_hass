from typing import Optional

from . import XR18Mixer
from homeassistant.components.binary_sensor import BinarySensorEntity
import logging
from homeassistant.helpers.entity import Entity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    xr18_mixer = hass.data[DOMAIN][entry.entry_id]
    channels = range(1, 17)
    async_add_entities([MuteChannelSensor(xr18_mixer, None),
        *(MuteChannelSensor(xr18_mixer, channel) for channel in channels)])

class MuteChannelSensor(BinarySensorEntity):
    def __init__(self, xr18_mixer: XR18Mixer, channel: Optional[int]):
        self._xr18_mixer = xr18_mixer
        self._channel = channel
        self._state = None

    @property
    def name(self):
        if self._channel == None:
            return f"Behringer XR18 Mixer Channel LR Mute State"
        return f"Behringer XR18 Mixer Channel {self._channel} Mute State"

    @property
    def unique_id(self):
        if self._channel == None:
            return f"{self._xr18_mixer.ip_address}_channel_lr_mute_state"
        return f"{self._xr18_mixer.ip_address}_channel_{self._channel}_mute_state"

    @property
    def is_on(self):
        return self._state

    async def async_update(self):
        self._state = await self._xr18_mixer.get_mute_channel(self._channel)
        _LOGGER.debug(f'Fader Mute {self._channel} value {self._state}')
