"""Luxafor Busy Tag Home Assistant integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import CONF_HOST, CONF_PORT, DOMAIN
from .coordinator import LuxaforCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SELECT, Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    coordinator = LuxaforCoordinator(hass, host, port)
    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_start_socketio()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _register_services(hass, coordinator)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator: LuxaforCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_stop_socketio()

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, "set_status")
        hass.services.async_remove(DOMAIN, "reconnect")

    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _register_services(hass: HomeAssistant, coordinator: LuxaforCoordinator) -> None:
    if hass.services.has_service(DOMAIN, "set_status"):
        return

    async def handle_set_status(call: ServiceCall) -> None:
        status = call.data["status"]
        valid_ids = coordinator.data.status_ids if coordinator.data else []
        if status not in valid_ids:
            _LOGGER.error("Invalid status '%s'. Valid options: %s", status, valid_ids)
            return
        await coordinator.async_set_status(status)

    async def handle_reconnect(_call: ServiceCall) -> None:
        await coordinator.async_reconnect_device()

    hass.services.async_register(
        DOMAIN,
        "set_status",
        handle_set_status,
        schema=vol.Schema({vol.Required("status"): cv.string}),
    )
    hass.services.async_register(DOMAIN, "reconnect", handle_reconnect)
