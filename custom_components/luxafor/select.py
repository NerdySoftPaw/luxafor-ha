"""Select entity: set Luxafor status."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LuxaforCoordinator
from .entity import LuxaforEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: LuxaforCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LuxaforStatusSelect(coordinator)])


class LuxaforStatusSelect(LuxaforEntity, SelectEntity):
    _attr_name = "Status"
    _attr_icon = "mdi:account-badge"

    def __init__(self, coordinator: LuxaforCoordinator) -> None:
        super().__init__(coordinator, "status")

    @property
    def options(self) -> list[str]:
        if not self.coordinator.data:
            return []
        return self.coordinator.data.status_ids

    @property
    def current_option(self) -> str | None:
        return self.coordinator.data.status if self.coordinator.data else None

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        status = self.coordinator.data.status_by_id(self.coordinator.data.status)
        return {
            "name": status.get("name"),
            "icon": status.get("icon"),
            "color": status.get("color"),
            "effective": self.coordinator.data.effective,
        }

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_status(option)
