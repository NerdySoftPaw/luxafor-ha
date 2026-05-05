"""Sensor: effective status of Luxafor."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LuxaforCoordinator
from .entity import LuxaforEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: LuxaforCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LuxaforEffectiveStatusSensor(coordinator)])


class LuxaforEffectiveStatusSensor(LuxaforEntity, SensorEntity):
    _attr_name = "Effective Status"
    _attr_icon = "mdi:led-on"

    def __init__(self, coordinator: LuxaforCoordinator) -> None:
        super().__init__(coordinator, "effective_status")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.effective if self.coordinator.data else None

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        status = self.coordinator.data.status_by_id(self.coordinator.data.effective)
        return {
            "name": status.get("name"),
            "icon": status.get("icon"),
            "color": status.get("color"),
        }
