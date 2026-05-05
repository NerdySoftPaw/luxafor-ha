"""Config flow for Luxafor integration."""
from __future__ import annotations

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_HOST, CONF_PORT, DEFAULT_HOST, DEFAULT_PORT, DOMAIN


async def _validate_connection(host: str, port: int) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://{host}:{port}/api/status",
            timeout=aiohttp.ClientTimeout(total=5),
        ) as r:
            r.raise_for_status()


class LuxaforConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            try:
                await _validate_connection(host, port)
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(f"luxafor_{host}_{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Luxafor @ {host}:{port}",
                    data={CONF_HOST: host, CONF_PORT: port},
                )

        schema = vol.Schema({
            vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return LuxaforOptionsFlow(config_entry)


class LuxaforOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            try:
                await _validate_connection(host, port)
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="", data={CONF_HOST: host, CONF_PORT: port})

        schema = vol.Schema({
            vol.Required(CONF_HOST, default=self._entry.data.get(CONF_HOST, DEFAULT_HOST)): str,
            vol.Required(CONF_PORT, default=self._entry.data.get(CONF_PORT, DEFAULT_PORT)): int,
        })
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
