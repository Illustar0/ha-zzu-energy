"""ZZU Energy 传感器平台."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.helpers.storage import Store
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZZUEnergyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ZZUEnergyDataUpdateCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置 ZZU Energy 传感器."""
    coordinator = entry.runtime_data

    if coordinator is None:
        return

    # 获取房间 ID
    room_ids = entry.options.get("room_ids", [])

    if not room_ids:
        return

    entities = []
    for room_id in room_ids:
        entities.append(ZZUEnergySensor(coordinator, entry, room_id))
        entities.append(ZZUEnergyConsumptionSensor(hass, coordinator, entry, room_id))
    async_add_entities(entities)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载 ZZU Energy 传感器平台."""
    return True


class ZZUEnergySensor(CoordinatorEntity[ZZUEnergyDataUpdateCoordinator], SensorEntity):
    """ZZU Energy 传感器."""

    _attr_device_class = None
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 2
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ZZUEnergyDataUpdateCoordinator,
        config_entry: ConfigEntry,
        room_id: str,
    ) -> None:
        """初始化传感器."""
        super().__init__(coordinator)
        self._room_id = room_id
        self._config_entry = config_entry

        self._attr_unique_id = f"{config_entry.entry_id}_{room_id.replace('-', '_')}"
        self._attr_object_id = f"zzu_energy_{room_id}"
        self._attr_name = "剩余电量"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_{room_id}")},
            name=room_id,
            manufacturer="郑州大学",
            model=f"宿舍电表 ({room_id})",
            sw_version="1.0.0",
            configuration_url="https://github.com/Illustar0/ZZU.Py",
            via_device=(DOMAIN, config_entry.entry_id),
        )

    @property
    def native_value(self) -> float | None:
        """返回传感器状态."""
        if self.coordinator.data is None:
            return None
        return round(self.coordinator.data.get(self._room_id), 2)

    @property
    def suggested_display_precision(self) -> int:
        """建议前端显示的小数位数."""
        return 2

    @property
    def available(self) -> bool:
        """返回实体是否可用."""
        return (
            super().available
            and self.coordinator.data is not None
            and self._room_id in self.coordinator.data
        )

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """返回额外状态属性."""
        return {
            "room_id": self._room_id,
            "last_update": f"{'Success' if self.coordinator.last_update_success else 'Failed'} | {self.coordinator.last_update_time.strftime('%Y-%m-%d %H:%M:%S')}",
        }


class ZZUEnergyConsumptionSensor(
    CoordinatorEntity[ZZUEnergyDataUpdateCoordinator], SensorEntity
):
    """ZZU Energy 消耗量传感器."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 3
    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: ZZUEnergyDataUpdateCoordinator,
        config_entry: ConfigEntry,
        room_id: str,
    ) -> None:
        """初始化消耗量传感器."""
        super().__init__(coordinator)
        self._room_id = room_id
        self.hass = hass
        self._config_entry = config_entry
        self._total_consumption = 0.0
        self._last_remaining = None

        # 持久化存储
        self._store = Store(
            self.hass,
            version=1,
            key=f"zzu_energy_consumption_{config_entry.entry_id}_{room_id}",
        )

        self._attr_unique_id = (
            f"{config_entry.entry_id}_{room_id.replace('-', '_')}_consumption"
        )
        self._attr_name = "总电量消耗"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_{room_id}")},
            name=room_id,
            manufacturer="郑州大学",
            model=f"宿舍电表 ({room_id})",
            sw_version="1.0.0",
            configuration_url="https://github.com/Illustar0/ZZU.Py",
            via_device=(DOMAIN, config_entry.entry_id),
        )

    async def async_added_to_hass(self) -> None:
        """当实体添加到 Home Assistant 时调用."""
        await super().async_added_to_hass()
        stored_data = await self._store.async_load()
        if stored_data:
            self._total_consumption = stored_data.get("total_consumption", 0.0)
            self._last_remaining = stored_data.get("last_remaining")

    async def _async_save_data(self) -> None:
        """保存数据到存储."""
        await self._store.async_save(
            {
                "total_consumption": self._total_consumption,
                "last_remaining": self._last_remaining,
            }
        )

    @property
    def native_value(self) -> float | None:
        """返回传感器状态."""
        if self.coordinator.data is None:
            return None

        current_remaining = self.coordinator.data.get(self._room_id)
        if current_remaining is None:
            return self._total_consumption

        if self._last_remaining is None:
            self._last_remaining = current_remaining
            self.hass.async_create_task(self._async_save_data())
            return self._total_consumption

        # 只有剩余电量下降时才增加消耗量
        if current_remaining < self._last_remaining:
            consumption_delta = self._last_remaining - current_remaining
            self._total_consumption += consumption_delta
            _LOGGER.debug(
                "房间 %s 消耗了 %.3f kWh 电量，总消耗: %.3f kWh",
                self._room_id,
                consumption_delta,
                self._total_consumption,
            )
            self.hass.async_create_task(self._async_save_data())

        self._last_remaining = current_remaining
        self.hass.async_create_task(self._async_save_data())
        return round(self._total_consumption, 2)

    @property
    def suggested_display_precision(self) -> int:
        """建议前端显示的小数位数."""
        return 2

    @property
    def available(self) -> bool:
        """返回实体是否可用."""
        return (
            super().available
            and self.coordinator.data is not None
            and self._room_id in self.coordinator.data
        )

    @property
    def extra_state_attributes(self) -> dict[str, str | float | None]:
        """返回额外状态属性."""
        return {
            "room_id": self._room_id,
            "last_remaining_energy": self._last_remaining,
            "last_update": f"{'Success' if self.coordinator.last_update_success else 'Failed'} | {self.coordinator.last_update_time.strftime('%Y-%m-%d %H:%M:%S')}",
        }
