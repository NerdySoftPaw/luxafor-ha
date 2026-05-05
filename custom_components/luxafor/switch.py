"""Switch entity: Luxafor device power (on/off)."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LuxaforCoordinator
from .entity import LuxaforEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: LuxaforCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LuxaforDevicePowerSwitch(coordinator)])


class LuxaforDevicePowerSwitch(LuxaforEntity, SwitchEntity):
    _attr_name = "Device Power"
    _attr_icon = "mdi:toggle-switch"

    def __init__(self, coordinator: LuxaforCoordinator) -> None:
        super().__init__(coordinator, "device_power")

    @property
    def is_on(self) -> bool:
        # "on" means the device is NOT in the off state
        return bool(self.coordinator.data and not self.coordinator.data.off)

    async def async_turn_on(self, **kwargs) -> None:
        if self.coordinator.data and self.coordinator.data.off:
            await self.coordinator.async_toggle_device()

    async def async_turn_off(self, **kwargs) -> None:
        if self.coordinator.data and not self.coordinator.data.off:
            await self.coordinator.async_toggle_device()
