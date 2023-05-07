from homeassistant.components.number import NumberEntity
from . import DOMAIN
from .xr18 import XR18Mixer

class VolumeNumber(NumberEntity):
    def __init__(self, mixer: XR18Mixer, channel: int):
        self.mixer = mixer
        self._channel = channel
        self._value = 0.0

    @property
    def unique_id(self):
        return f"xr18_volume_number_{self._channel}"

    @property
    def name(self):
        return f"XR18 Channel {self._channel} Volume"

    @property
    def value(self) -> float:
        return self._value

    @property
    def min_value(self):
        return 0.0

    @property
    def max_value(self):
        return 1.0

    @property
    def step(self):
        return 0.1

    async def async_set_value(self, value: float):
        await self.mixer.set_fader_level(self._channel, value)
        self._value = value
        self.async_write_ha_state()

    async def async_update(self):
        self._value = await self.mixer.get_fader_level(self._channel)

async def async_setup_entry(hass, config_entry, async_add_entities):
    mixer = hass.data[DOMAIN][config_entry.entry_id]

    # Create volume number entities for all channels (assumes 18 channels)
    volume_numbers = [VolumeNumber(mixer, channel) for channel in range(1, 19)]

    # Register the entities with Home Assistant
    async_add_entities(volume_numbers, update_before_add=True)
