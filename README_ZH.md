# ZZU Energy for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Illustar0/ha-zzu-energy.svg)](https://github.com/Illustar0/ha-zzu-energy/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](README.md) | 中文

---

## 📝 简介

ZZU Energy 是一个专为郑州大学学生开发的 Home Assistant 自定义集成，用于监控宿舍电量消耗。它与 Home Assistant 的能源仪表盘完美集成，提供实时的电量监控和管理功能。

## ✨ 功能特点

- 🔐 **安全认证**：使用郑州大学统一认证系统 (CAS) 进行安全登录
- 🏠 **多房间监控**：支持监控多个宿舍房间的电量
- ⚡ **实时更新**：每5分钟自动更新电量数据
- 📊 **能源仪表盘集成**：与 Home Assistant 能源仪表盘完美集成
- 🌍 **多语言支持**：支持中文和英文界面
- ✨ **自动令牌刷新**：自动处理认证令牌过期
- 📈 **历史数据**：追踪电量使用历史
- 🔔 **自动化支持**：基于电量消耗创建自动化

## 📦 安装方法

### 方法一：通过 HACS 安装（推荐）

1. 在 Home Assistant 中打开 HACS
2. 点击"集成"
3. 点击右上角三点菜单
4. 选择"自定义仓库"
5. 添加仓库地址：`https://github.com/Illustar0/ha-zzu-energy`
6. 选择类别："Integration"
7. 点击"添加"
8. 搜索"郑州大学宿舍电费监控"并安装
9. 重启 Home Assistant

### 方法二：手动安装

1. 从 [GitHub Releases](https://github.com/Illustar0/ha-zzu-energy/releases) 下载最新版本
2. 解压并复制 `custom_components/zzu_energy` 文件夹到 Home Assistant 的 `custom_components/` 目录
3. 重启 Home Assistant

## ⚙️ 配置说明

### 初始设置

1. 进入 Home Assistant **设置** > **设备与服务**
2. 点击**添加集成**
3. 搜索"ZZU Energy"
4. 输入您的郑州大学账号密码
5. 提交完成初始配置

### 添加房间

初始设置完成后，添加要监控的房间：

1. 在集成页面点击**配置**
2. 选择**添加**操作
3. 输入房间ID（格式：`areaid-buildingid--unitid-roomid`）
4. 提交添加房间
5. 重复添加更多房间
6. 选择**保存**完成配置

### 房间ID格式

房间ID格式为：`areaid-buildingid--unitid-roomid`

示例：`99-12--33-404`
- 区域ID：99
- 楼栋ID：12
- 单元ID：33
- 房间号：404

您可以通过 [ZZU.Py](https://github.com/Illustar0/ZZU.Py) 获取正确的房间ID。

## 📄 许可证

本项目基于 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📞 支持

- [GitHub Issues](https://github.com/Illustar0/ha-zzu-energy/issues)
- [项目文档](https://github.com/Illustar0/ha-zzu-energy/wiki)

## ⭐ 星标历史

如果您觉得这个集成有用，请给项目一个 ⭐ 星标！