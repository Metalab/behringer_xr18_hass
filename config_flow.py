import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_HOST, CONF_PORT
from . import (CONF_XR18_SWITCH, DOMAIN)

DEFAULT_PORT = 10024

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_XR18_SWITCH): str
    }
)

@config_entries.HANDLERS.register(DOMAIN)
class BehringerXR18ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            existing_entry = await self.async_set_unique_id(user_input[CONF_HOST])
            if existing_entry:
                return self.async_abort(reason="already_configured")

            return self.async_create_entry(title=f"Behringer XR18 Mixer ({user_input[CONF_HOST]})", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
