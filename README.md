# Luxafor Busy Tag — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for the [Luxafor Busy Tag](https://luxafor.com/busy-tag/) via the [luxafor-api](https://github.com/kevkugler/luxafor-api) REST + Socket.IO backend.

## Features

- **Select entity** — choose your current status (fetched dynamically from the API)
- **Sensor entity** — shows the *effective* status (may differ from manual when overridden)
- **Binary sensor** — tracks device online/offline state
- **Switch** — turn the Busy Tag on or off
- **Real-time updates** via Socket.IO push (no polling lag)
- **Services** — set status and trigger device reconnect from automations

## Requirements

- [luxafor-api](https://github.com/kevkugler/luxafor-api) running and reachable on your network
- Home Assistant 2024.1.0 or newer

## Installation

### Via HACS (recommended)

1. Open HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/kevkugler/luxafor-ha` as type **Integration**
3. Install **Luxafor Busy Tag**
4. Restart Home Assistant

### Manual

```bash
cp -r custom_components/luxafor /config/custom_components/
# restart Home Assistant
```

## Configuration

1. Go to **Settings → Integrations → Add Integration**
2. Search for **Luxafor Busy Tag**
3. Enter the host/IP and port of your `luxafor-api` instance

## Entities

| Entity | Type | Description |
|--------|------|-------------|
| `select.luxafor_status` | Select | Set the current status |
| `sensor.luxafor_effective_status` | Sensor | Currently active status |
| `binary_sensor.luxafor_device_online` | Binary Sensor | Device connectivity |
| `switch.luxafor_device_power` | Switch | Turn device on/off |

## Services

### `luxafor.set_status`

Set the status programmatically (e.g. from an automation).

```yaml
service: luxafor.set_status
data:
  status: focus
```

Valid status IDs are fetched from the API's `/api/statuses` endpoint at startup.

### `luxafor.reconnect`

Trigger a reconnect attempt to the physical device.

```yaml
service: luxafor.reconnect
```

## Architecture

- **Polling interval:** 30 seconds (fallback)
- **Push updates:** Socket.IO events `status_changed` + `busytag_changed` trigger immediate refresh
- **Status list:** Fetched dynamically from `/api/statuses` — no hardcoded values
