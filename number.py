from homeassistant.components.number import NumberEntity
from . import DOMAIN
from .xr18 import XR18Mixer


class VolumeNumber(NumberEntity):
    def __init__(self, mixer: XR18Mixer, channel: int):
        self.mixer = mixer
        self._channel = channel
        self._value = 0.0
        mixer.subscribe_fader(channel, self.update_value)

    def update_value(self, value: float):
        self._value = value
        self.async_write_ha_state()

    @property
    def should_poll(self):
        return False

    @property
    def unique_id(self):
        return f"xr18_volume_number_{self._channel}"

    @property
    def name(self):
        return f"XR18 Channel {self._channel} Volume"

    @property
    def native_value(self) -> float:
        return self._value

    @property
    def native_min_value(self):
        return 0.0

    @property
    def native_max_value(self):
        return 1.0

    @property
    def native_step(self):
        return 0.1

    def set_native_value(self, value: float):
        self.mixer.set_fader_level(self._channel, value)
        self._value = value
        self.async_write_ha_state()


async def async_setup_entry(hass, config_entry, async_add_entities):
    mixer = hass.data[DOMAIN][config_entry.entry_id]

    # Create volume number entities for all channels (assumes 18 channels)
    volume_numbers = [VolumeNumber(mixer, channel) for channel in range(18)]

    # Register the entities with Home Assistant
    async_add_entities(volume_numbers, update_before_add=True)
