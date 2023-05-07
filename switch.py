from homeassistant.components.switch import SwitchEntity
from .xr18 import XR18Mixer
from . import DOMAIN

class MuteSwitch(SwitchEntity):
    def __init__(self, mixer: XR18Mixer, channel: int):
        self.mixer = mixer
        self._channel = channel
        self._state = False

    @property
    def unique_id(self):
        return f"xr18_mute_switch_{self._channel}"

    @property
    def name(self):
        return f"XR18 Channel {self._channel} Mute Switch"

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        await self.mixer.mute_channel(self._channel, True)
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.mixer.mute_channel(self._channel, False)
        self._state = False
        self.async_write_ha_state()

    async def async_update(self):
        self._state = await self.mixer.get_mute_channel(self._channel)

async def async_setup_entry(hass, config_entry, async_add_entities):
    mixer = hass.data[DOMAIN][config_entry.entry_id]

    # Create volume number entities for all channels (assumes 18 channels)
    volume_numbers = [MuteSwitch(mixer, channel) for channel in range(1, 19)]

    # Register the entities with Home Assistant
    async_add_entities(volume_numbers, update_before_add=True)
