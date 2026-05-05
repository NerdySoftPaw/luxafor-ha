"""Image entity: current Luxafor status image."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LuxaforCoordinator
from .entity import LuxaforEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: LuxaforCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LuxaforStatusImage(coordinator, hass)])


class LuxaforStatusImage(LuxaforEntity, ImageEntity):
    _attr_name = "Status Image"
    _attr_content_type = "image/png"

    def __init__(self, coordinator: LuxaforCoordinator, hass: HomeAssistant) -> None:
        LuxaforEntity.__init__(self, coordinator, "status_image")
        ImageEntity.__init__(self, hass)
        self._last_updated: datetime = datetime.now()
        self._last_effective: str = ""

    @property
    def image_url(self) -> str | None:
        if not self.coordinator.data:
            return None
        return f"{self.coordinator.base_url}/images/{self.coordinator.data.effective}.png"

    @property
    def image_last_updated(self) -> datetime:
        return self._last_updated

    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data:
            effective = self.coordinator.data.effective
            if effective != self._last_effective:
                self._last_effective = effective
                self._last_updated = datetime.now()
        super()._handle_coordinator_update()
