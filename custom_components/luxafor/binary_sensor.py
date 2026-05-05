"""Binary sensor: Luxafor device online/offline."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LuxaforCoordinator
from .entity import LuxaforEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: LuxaforCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LuxaforDeviceOnlineSensor(coordinator)])


class LuxaforDeviceOnlineSensor(LuxaforEntity, BinarySensorEntity):
    _attr_name = "Device Online"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: LuxaforCoordinator) -> None:
        super().__init__(coordinator, "device_online")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data and self.coordinator.data.online)

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data or not self.coordinator.data.last_seen:
            return {}
        return {"last_seen": datetime.fromtimestamp(self.coordinator.data.last_seen).isoformat()}
