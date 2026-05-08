"""DataUpdateCoordinator with REST polling and Socket.IO push."""
from __future__ import annotations

import asyncio
import dataclasses
import logging
from dataclasses import dataclass, field
from datetime import timedelta

import aiohttp
import socketio

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

POLL_INTERVAL = timedelta(seconds=30)


@dataclass
class LuxaforData:
    status: str
    effective: str
    online: bool
    last_seen: float | None
    off: bool
    pending_off: bool = False
    statuses: list[dict] = field(default_factory=list)

    @property
    def status_ids(self) -> list[str]:
        return [s["id"] for s in self.statuses]

    def status_by_id(self, status_id: str) -> dict:
        return next((s for s in self.statuses if s["id"] == status_id), {})


class LuxaforCoordinator(DataUpdateCoordinator[LuxaforData]):
    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=POLL_INTERVAL)
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self._statuses: list[dict] = []
        self._sio: socketio.AsyncClient | None = None
        self._sio_task: asyncio.Task | None = None

    async def _async_update_data(self) -> LuxaforData:
        session = async_get_clientsession(self.hass)
        try:
            if not self._statuses:
                async with session.get(
                    f"{self.base_url}/api/statuses",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as r:
                    r.raise_for_status()
                    self._statuses = await r.json()

            async with session.get(
                f"{self.base_url}/api/state",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as r:
                r.raise_for_status()
                data = await r.json()

        except Exception as err:
            raise UpdateFailed(f"Cannot reach Luxafor API: {err}") from err

        return LuxaforData(
            status=data.get("status", ""),
            effective=data.get("effective", ""),
            online=data.get("online", False),
            last_seen=data.get("last_seen"),
            off=data.get("off", False),
            pending_off=data.get("pending_off", False),
            statuses=self._statuses,
        )

    async def async_set_status(self, status_id: str) -> None:
        session = async_get_clientsession(self.hass)
        async with session.put(
            f"{self.base_url}/api/status",
            json={"status": status_id},
            timeout=aiohttp.ClientTimeout(total=5),
        ) as r:
            r.raise_for_status()
        # No manual refresh — socket.io push updates state

    async def async_toggle_device(self) -> None:
        session = async_get_clientsession(self.hass)
        async with session.post(
            f"{self.base_url}/api/busytag/toggle",
            timeout=aiohttp.ClientTimeout(total=5),
        ) as r:
            r.raise_for_status()
        # No manual refresh — socket.io push updates state

    async def async_reconnect_device(self) -> None:
        session = async_get_clientsession(self.hass)
        async with session.post(
            f"{self.base_url}/api/busytag/command",
            json={"action": "reconnect"},
            timeout=aiohttp.ClientTimeout(total=5),
        ) as r:
            r.raise_for_status()

    async def async_start_socketio(self) -> None:
        self._sio = socketio.AsyncClient(reconnection=True, reconnection_attempts=0)

        @self._sio.event
        async def status_changed(data: dict) -> None:
            if self.data:
                self.data = dataclasses.replace(
                    self.data,
                    status=data.get("status", self.data.status),
                    effective=data.get("effective", self.data.effective),
                )
                self.async_update_listeners()
            else:
                await self.async_request_refresh()

        @self._sio.event
        async def busytag_changed(data: dict) -> None:
            if self.data:
                self.data = dataclasses.replace(
                    self.data,
                    online=data.get("online", self.data.online),
                    last_seen=data.get("last_seen", self.data.last_seen),
                    off=data.get("off", self.data.off),
                    pending_off=data.get("pending_off", self.data.pending_off),
                )
                self.async_update_listeners()
            else:
                await self.async_request_refresh()

        @self._sio.event
        async def connect_error(data: object) -> None:
            _LOGGER.warning("Socket.IO connect error: %s", data)

        async def _connect_loop() -> None:
            while True:
                try:
                    await self._sio.connect(self.base_url, transports=["websocket", "polling"])
                    await self._sio.wait()
                except Exception as err:
                    _LOGGER.debug("Socket.IO disconnected (%s), retrying in 10s", err)
                    await asyncio.sleep(10)

        self._sio_task = asyncio.create_task(_connect_loop())

    async def async_stop_socketio(self) -> None:
        if self._sio_task:
            self._sio_task.cancel()
            try:
                await self._sio_task
            except asyncio.CancelledError:
                pass
        if self._sio and self._sio.connected:
            await self._sio.disconnect()
