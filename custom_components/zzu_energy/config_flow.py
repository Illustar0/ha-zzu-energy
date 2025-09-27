"""ZZU Energy 配置流程."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr

from zzupy.aio.app import CASClient
from zzupy.exception import LoginError, NetworkError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理 ZZU Energy 配置流程."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """处理初始步骤."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            await self.async_set_unique_id(f"{DOMAIN}_{username}")
            self._abort_if_unique_id_configured()
            try:
                cas_client = await self.hass.async_add_executor_job(
                    lambda: CASClient(username, password)
                )
                await cas_client.login()

                user_token = cas_client.user_token
                refresh_token = cas_client.refresh_token

                if not user_token or not refresh_token:
                    errors["base"] = "token_error"
                else:
                    return self.async_create_entry(
                        title=f"ZZU Energy ({username})",
                        data={
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
                            "user_token": user_token,
                            "refresh_token": refresh_token,
                        },
                    )

                await cas_client.close()
            except LoginError:
                errors["base"] = "invalid_auth"
            except NetworkError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """创建选项流程."""
        return OptionsFlowHandler()

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            await self.async_set_unique_id(f"{DOMAIN}_{username}")
            self._abort_if_unique_id_mismatch()
            try:
                cas_client = await self.hass.async_add_executor_job(
                    lambda: CASClient(username, password)
                )
                await cas_client.login()

                user_token = cas_client.user_token
                refresh_token = cas_client.refresh_token

                if not user_token or not refresh_token:
                    errors["base"] = "token_error"
                else:
                    return self.async_update_reload_and_abort(
                        entry=self._get_reconfigure_entry(),
                        data={
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
                            "user_token": user_token,
                            "refresh_token": refresh_token,
                        },
                    )

                await cas_client.close()
            except LoginError:
                errors["base"] = "invalid_auth"
            except NetworkError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reconfigure", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """处理 ZZU Energy 选项流程."""

    def __init__(self) -> None:
        """初始化选项流程."""
        self.temp_room_ids: list[str] = []

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """管理选项."""
        self.temp_room_ids = list(self.config_entry.options.get("room_ids", []))
        return await self.async_step_room_management()

    async def async_step_room_management(
        self, user_input: dict[str, Any] | None = None
    ):
        """显示房间管理主菜单."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add_room":
                return await self.async_step_add_room()
            if action == "remove_room":
                if not self.temp_room_ids:
                    return await self.async_step_room_management()
                return await self.async_step_remove_room()
            if action == "finish":
                await self._cleanup_removed_room_devices()
                return self.async_create_entry(
                    title="", data={"room_ids": self.temp_room_ids}
                )

        description_placeholders = {
            "current_rooms": ", ".join(self.temp_room_ids)
            if self.temp_room_ids
            else "无房间配置",
            "room_count": str(len(self.temp_room_ids)),
        }

        return self.async_show_form(
            step_id="room_management",
            data_schema=vol.Schema(
                {vol.Required("action"): vol.In(["add_room", "remove_room", "finish"])}
            ),
            description_placeholders=description_placeholders,
        )

    async def async_step_add_room(self, user_input: dict[str, Any] | None = None):
        """处理添加房间."""
        errors: dict[str, str] = {}
        if user_input is not None:
            room_id = user_input.get("room_id", "").strip()

            if not room_id:
                errors["base"] = "room_id_empty"
            elif room_id in self.temp_room_ids:
                errors["base"] = "room_already_exists"
            elif not self._validate_room_id_format(room_id):
                errors["base"] = "invalid_room_format"
            else:
                self.temp_room_ids.append(room_id)
                return await self.async_step_room_management()

        return self.async_show_form(
            step_id="add_room",
            data_schema=vol.Schema({vol.Required("room_id"): str}),
            errors=errors,
            description_placeholders={
                "current_rooms": ", ".join(self.temp_room_ids)
                if self.temp_room_ids
                else "无",
            },
        )

    async def async_step_remove_room(self, user_input: dict[str, Any] | None = None):
        """处理删除房间."""
        if user_input is not None:
            room_to_remove = user_input.get("room_id")
            if room_to_remove in self.temp_room_ids:
                self.temp_room_ids.remove(room_to_remove)
            return await self.async_step_room_management()

        return self.async_show_form(
            step_id="remove_room",
            data_schema=vol.Schema(
                {vol.Required("room_id"): vol.In(self.temp_room_ids)}
            ),
            description_placeholders={"current_rooms": ", ".join(self.temp_room_ids)},
        )

    @staticmethod
    def _validate_room_id_format(room_id: str) -> bool:
        """验证房间 ID 格式."""
        if not room_id or "--" not in room_id:
            return False
        parts = room_id.split("--")
        if len(parts) != 2:
            return False
        left_part, right_part = parts
        return bool(left_part and right_part and "-" in left_part and "-" in right_part)

    async def _cleanup_removed_room_devices(self) -> None:
        """清理已删除房间的设备."""
        if not self.hass:
            return

        device_registry = dr.async_get(self.hass)
        current_room_ids = set(self.config_entry.options.get("room_ids", []))
        new_room_ids = set(self.temp_room_ids)
        removed_room_ids = current_room_ids - new_room_ids

        for room_id in removed_room_ids:
            device_id = (DOMAIN, f"{self.config_entry.entry_id}_{room_id}")
            device = device_registry.async_get_device(identifiers={device_id})
            if device:
                device_registry.async_remove_device(device.id)
