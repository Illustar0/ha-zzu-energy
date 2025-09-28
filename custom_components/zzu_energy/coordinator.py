"""ZZU Energy 数据更新协调器."""

from __future__ import annotations

import asyncio
import datetime
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt

from zzupy.aio.app import CASClient, ECardClient
from zzupy.exception import LoginError, NetworkError, NotLoggedInError

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ZZUEnergyDataUpdateCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """管理获取 ZZU Energy 数据的协调器."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """初始化协调器."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
            always_update=False,
        )
        self.config_entry = config_entry
        self._cas_client: CASClient | None = None
        self._ecard_client: ECardClient | None = None
        self.last_update_time: datetime.datetime | None = None

    async def _async_setup(self) -> None:
        """设置协调器."""
        username = self.config_entry.data[CONF_USERNAME]
        password = self.config_entry.data[CONF_PASSWORD]

        self._cas_client = await self.hass.async_add_executor_job(
            CASClient, username, password
        )

        user_token = self.config_entry.data.get("user_token")
        refresh_token = self.config_entry.data.get("refresh_token")
        if user_token and refresh_token:
            self._cas_client.set_token(user_token, refresh_token)
        try:
            await self._cas_client.login()

            new_user_token = self._cas_client.user_token
            new_refresh_token = self._cas_client.refresh_token

            if new_user_token != self.config_entry.data.get(
                "user_token"
            ) or new_refresh_token != self.config_entry.data.get("refresh_token"):
                new_data = {
                    **self.config_entry.data,
                    "user_token": new_user_token,
                    "refresh_token": new_refresh_token,
                }
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=new_data
                )

        except (LoginError, NetworkError) as err:
            raise ConfigEntryAuthFailed(f"Failed to login to CAS: {err}") from err

        self._ecard_client = await self.hass.async_add_executor_job(
            ECardClient, self._cas_client
        )
        await self._ecard_client.login()
        await self._create_main_device()

    async def _async_update_data(self) -> dict[str, float]:
        """获取 API 数据."""
        self.last_update_time = dt.now()
        room_ids = self.config_entry.options.get("room_ids", [])

        if not room_ids:
            return {}

        energy_data: dict[str, float] = {}
        tasks = [self._fetch_room_energy(room_id) for room_id in room_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for room_id, result in zip(room_ids, results, strict=True):
            if isinstance(result, Exception):
                _LOGGER.warning("Failed to fetch data for room %s: %s", room_id, result)
                if self.data and room_id in self.data:
                    energy_data[room_id] = self.data[room_id]
            else:
                energy_data[room_id] = result

        if not energy_data and room_ids:
            raise UpdateFailed("Failed to fetch energy data for any room")

        return energy_data

    async def _fetch_room_energy(self, room_id: str) -> float:
        """获取指定房间的能耗数据."""
        if self._ecard_client is None:
            raise UpdateFailed("ECard client not initialized")

        try:
            return await self._ecard_client.get_remaining_energy(room_id)
        except (LoginError, NetworkError, NotLoggedInError) as err:
            _LOGGER.debug("Token expired for room %s, re-authenticating: %s", room_id, err)
            await self._cas_client.login()
            await self._ecard_client.login()
            return await self._ecard_client.get_remaining_energy(room_id)

    async def async_shutdown(self) -> None:
        """关闭协调器."""
        if self._ecard_client:
            await self._ecard_client.close()
        if self._cas_client:
            await self._cas_client.close()

    async def _create_main_device(self) -> None:
        """创建主设备."""
        device_registry = dr.async_get(self.hass)
        username = self.config_entry.data[CONF_USERNAME]

        device_registry.async_get_or_create(
            config_entry_id=self.config_entry.entry_id,
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=f"ZZU Energy ({username})",
            manufacturer="郑州大学",
            model="能耗监控系统",
            sw_version="1.0.0",
            configuration_url="https://github.com/Illustar0/ha-zzu-energy",
        )
