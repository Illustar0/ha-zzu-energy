from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN as DOMAIN, PLATFORMS
from .coordinator import ZZUEnergyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry[ZZUEnergyDataUpdateCoordinator]
) -> bool:
    """设置配置条目"""
    coordinator = ZZUEnergyDataUpdateCoordinator(hass, entry)
    entry.runtime_data = coordinator

    await coordinator._async_setup()
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("ZZU Energy setup completed")
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry[ZZUEnergyDataUpdateCoordinator]
) -> bool:
    """卸载配置条目"""
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    except ValueError as e:
        if "Config entry was never loaded" in str(e):
            unload_ok = True
        else:
            raise

    if hasattr(entry, "runtime_data") and entry.runtime_data:
        await entry.runtime_data.async_shutdown()
        entry.runtime_data = None

    _LOGGER.info("ZZU Energy unloaded")
    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant, entry: ConfigEntry[ZZUEnergyDataUpdateCoordinator]
) -> None:
    """重新加载配置条目"""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
