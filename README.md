# UPGRAIT HeatControl for Home Assistant

Home Assistant integration for UPGRAIT HeatControl.

This repository is the HACS/custom-integration distribution of `upgrait_heatcontrol`.
The protocol client dependency is published separately on PyPI as `upgrait-heatcontrol-api`.

## Features

- local setup via config flow
- Zeroconf discovery via `_upgrait-hc._tcp.local.`
- PIN-based pairing with the UHC
- encrypted websocket transport via the external API package
- sensors, binary sensors, switches, and numbers for the first HeatControl entity set

## Installation via HACS

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository of type `Integration`.
3. Search for `UPGRAIT HeatControl` and install it.
4. Restart Home Assistant.
5. Add the integration from `Settings -> Devices & services`.

## Development

This repository is intended for HACS/custom installation.
The long-term goal is inclusion in Home Assistant Core, which will happen through a separate upstream pull request to `home-assistant/core`.

## Support

- Issues: `https://github.com/UPGRAITgmbh/ha-upgrait-heatcontrol/issues`
- Product website: `https://upgrait.com/heatcontrol/`
