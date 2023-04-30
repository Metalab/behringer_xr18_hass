from typing import Optional

from . import XR18Mixer
from homeassistant.components.sensor import SensorEntity
import logging
from homeassistant.helpers.entity import Entity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    xr18_mixer = hass.data[DOMAIN][entry.entry_id]
    channels = range(1, 17)
    async_add_entities([FaderLevelSensor(xr18_mixer, None),
        *(FaderLevelSensor(xr18_mixer, channel) for channel in channels)])

class FaderLevelSensor(SensorEntity):
    def __init__(self, xr18_mixer: XR18Mixer, channel: Optional[int]):
        self._xr18_mixer = xr18_mixer
        self._channel = channel
        self._state = None

    @property
    def name(self):
        if self._channel == None:
            return f"Behringer XR18 Mixer Channel LR Fader Level"
        return f"Behringer XR18 Mixer Channel {self._channel} Fader Level"

    @property
    def unique_id(self):
        if self._channel == None:
            return f"{self._xr18_mixer.ip_address}_channel_lr_fader_level"
        return f"{self._xr18_mixer.ip_address}_channel_{self._channel}_fader_level"

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def state(self):
        return self._state

    async def async_update(self):
        self._state = await self._xr18_mixer.get_fader_level(self._channel)
        _LOGGER.debug(f'Fader {self._channel} value {self._state}')
