# ZZU Energy - Home Assistant 集成

ZZU Energy 是一个为郑州大学学生开发的 Home Assistant 自定义集成，用于监控宿舍电量数据并完美接入 Home Assistant 的能源仪表盘。

## 功能特性

- 🔐 **安全认证**: 使用郑州大学统一认证系统 (CAS) 进行安全登录
- 🏠 **多房间监控**: 支持监控多个房间的电量数据
- ⚡ **实时更新**: 每5分钟自动更新电量数据
- 📊 **能源仪表盘**: 完美接入 Home Assistant 能源仪表盘
- 🌍 **多语言支持**: 支持中文和英文界面
- ✨ **自动令牌刷新**: 自动处理认证令牌过期和刷新

## 安装

### 方法一：HACS 安装 (推荐)
1. 在 HACS 中添加自定义仓库
2. 搜索 "ZZU Energy" 并安装
3. 重启 Home Assistant

### 方法二：手动安装
1. 将 `custom_components/zzu_energy` 目录复制到您的 Home Assistant 配置目录下的 `custom_components/` 文件夹中
2. 重启 Home Assistant
3. 在 Home Assistant 中添加集成

## 配置

### 初始设置
1. 在 Home Assistant 中进入 **设置** > **设备与服务**
2. 点击 **添加集成**
3. 搜索 "ZZU Energy"
4. 输入您的郑州大学账号和密码
5. 点击提交完成初始配置

### 房间管理
初始配置完成后，您需要添加要监控的房间：

1. 在集成页面点击 **配置**
2. 选择 **添加** 操作
3. 输入房间ID（格式：`areaid-buildingid--unitid-roomid`）
4. 点击提交添加房间
5. 重复步骤添加更多房间
6. 选择 **保存** 操作完成配置

### 房间ID格式说明
房间ID的格式为：`areaid-buildingid--unitid-roomid`

例如：`99-12--33-404` 表示：
- 区域ID：99
- 楼栋ID：12  
- 单元ID：33
- 房间号：404

您可以通过郑州大学一卡通系统或咨询宿管获取正确的房间ID。

## 使用

### 传感器实体
集成会为每个配置的房间创建一个电量传感器实体：
- **实体ID**: `sensor.room_{room_id}_energy`
- **设备类别**: 能源 (energy)
- **状态类别**: 总计递增 (total_increasing)
- **单位**: 千瓦时 (kWh)

### 能源仪表盘集成
1. 进入 Home Assistant **能源** 页面
2. 在 **电网消耗** 部分添加传感器
3. 选择您的房间电量传感器
4. 保存配置

现在您可以在能源仪表盘中查看详细的电量消耗统计、历史趋势和成本分析。

### 自动化示例
您可以创建自动化来监控电量变化：

```yaml
automation:
  - alias: "低电量提醒"
    trigger:
      - platform: numeric_state
        entity_id: sensor.room_99_12_33_404_energy
        below: 5
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "宿舍电量不足，剩余 {{ states('sensor.room_99_12_33_404_energy') }} 度"
```

## 故障排除

### 常见问题

**Q: 登录失败，提示 "invalid_auth"**  
A: 检查您的郑州大学账号密码是否正确，确保能正常登录郑州大学相关系统。

**Q: 无法连接服务器，提示 "cannot_connect"**  
A: 检查网络连接，确保能访问郑州大学服务器。可能需要连接校园网或VPN。

**Q: 房间ID无效**  
A: 确认房间ID格式正确 (`areaid-buildingid--unitid-roomid`)，可以通过一卡通系统查询正确的房间ID。

**Q: 传感器数据不更新**  
A: 检查集成日志，可能是认证令牌过期或网络问题。集成会自动重试和刷新令牌。

**Q: 能源仪表盘中看不到数据**  
A: 确保传感器的设备类别设置为 "energy"，状态类别为 "total_increasing"。

### 调试日志
如需查看详细日志，在 `configuration.yaml` 中添加：

```yaml
logger:
  logs:
    custom_components.zzu_energy: debug
    zzupy: debug
```

## 安全性

- 集成使用郑州大学官方认证系统，不存储明文密码
- 认证令牌安全存储在 Home Assistant 配置中
- 所有网络通信使用 HTTPS 加密
- 定期自动刷新认证令牌，无需手动重新登录

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本电量监控功能
- 支持多房间管理
- 完美接入能源仪表盘
- 多语言支持

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个集成。

## 许可证

本项目基于 ZZU.Py 库开发，请遵守相应的开源许可证。

## 支持

如果您觉得这个集成有用，请给项目一个 ⭐ 星标！

---

**注意**: 本集成仅供郑州大学学生学习和使用，请遵守学校相关规定。