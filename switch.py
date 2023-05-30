from homeassistant.components.switch import SwitchEntity
from .xr18 import XR18Mixer
from . import DOMAIN


class MuteSwitch(SwitchEntity):
    def __init__(self, mixer: XR18Mixer, channel: int):
        self.mixer = mixer
        self._channel = channel
        self._state = False
        self._available = False
        mixer.subscribe_mute(channel, self.update_value)
        mixer.subscribe_available(self.update_available)

    def update_value(self, value: bool):
        self._state = value
        self.async_write_ha_state()

    def update_available(self, value: bool):
        self._available = value
        self.async_write_ha_state()

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._available

    @property
    def unique_id(self):
        return f"xr18_mute_switch_{self._channel}"

    @property
    def name(self):
        return f"XR18 Channel {self._channel} Mute Switch"

    @property
    def is_on(self) -> bool:
        return self._state

    def turn_on(self, **kwargs):
        self.mixer.mute_channel(self._channel, True)
        self._state = True
        self.async_write_ha_state()

    def turn_off(self, **kwargs):
        self.mixer.mute_channel(self._channel, False)
        self._state = False
        self.async_write_ha_state()


async def async_setup_entry(hass, config_entry, async_add_entities):
    mixer = hass.data[DOMAIN][config_entry.entry_id]

    # Create volume number entities for all channels (assumes 18 channels)
    volume_numbers = [MuteSwitch(mixer, channel) for channel in range(18)]

    # Register the entities with Home Assistant
    async_add_entities(volume_numbers, update_before_add=True)
