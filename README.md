# ZZU Energy for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Illustar0/ha-zzu-energy.svg)](https://github.com/Illustar0/ha-zzu-energy/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

English | [中文](README_ZH.md)

---

## 📝 Description

ZZU Energy is a custom Home Assistant integration designed for Zhengzhou University students to monitor dormitory electricity consumption. It seamlessly integrates with Home Assistant's Energy Dashboard, providing real-time electricity monitoring and management capabilities.

## ✨ Features

- 🔐 **Secure Authentication**: Uses Zhengzhou University's unified authentication system (CAS)
- 🏠 **Multi-room Monitoring**: Support for monitoring multiple dormitory rooms
- ⚡ **Real-time Updates**: Automatically updates electricity data every 5 minutes
- 📊 **Energy Dashboard Integration**: Perfect integration with Home Assistant's Energy Dashboard
- 🌍 **Multi-language Support**: Available in Chinese and English
- ✨ **Automatic Token Refresh**: Handles authentication token expiration automatically
- 📈 **Historical Data**: Track electricity usage over time
- 🔔 **Automation Ready**: Create automations based on electricity consumption

## 📦 Installation

### Method 1: HACS Installation (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots menu in the top right corner
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/Illustar0/ha-zzu-energy`
6. Select category: "Integration"
7. Click "Add"
8. Search for "ZZU Energy" and install
9. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/Illustar0/ha-zzu-energy/releases)
2. Extract and copy the `custom_components/zzu_energy` folder to your Home Assistant's `custom_components/` directory
3. Restart Home Assistant

## ⚙️ Configuration

### Initial Setup

1. Go to **Settings** > **Devices & Services** in Home Assistant
2. Click **Add Integration**
3. Search for "ZZU Energy"
4. Enter your Zhengzhou University credentials
5. Submit to complete initial configuration

### Adding Rooms

After initial setup, add rooms to monitor:

1. Click **Configure** on the integration page
2. Select **Add** action
3. Enter room ID (format: `areaid-buildingid--unitid-roomid`)
4. Submit to add the room
5. Repeat for additional rooms
6. Select **Save** to finalize configuration

### Room ID Format

Room ID follows the pattern: `areaid-buildingid--unitid-roomid`

Example: `99-12--33-404`
- Area ID: 99
- Building ID: 12
- Unit ID: 33
- Room Number: 404

You can obtain the correct room ID through [ZZU.Py](https://github.com/Illustar0/ZZU.Py).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- [GitHub Issues](https://github.com/Illustar0/ha-zzu-energy/issues)
- [Documentation](https://github.com/Illustar0/ha-zzu-energy/wiki)

## ⭐ Star History

If you find this integration useful, please give it a star! ⭐