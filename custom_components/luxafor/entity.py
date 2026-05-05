"""Base entity for Luxafor integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LuxaforCoordinator


class LuxaforEntity(CoordinatorEntity[LuxaforCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: LuxaforCoordinator, unique_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"luxafor_{coordinator.host}_{unique_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="Luxafor Busy Tag",
            manufacturer="Luxafor",
            model="Busy Tag",
            configuration_url=coordinator.base_url,
        )
