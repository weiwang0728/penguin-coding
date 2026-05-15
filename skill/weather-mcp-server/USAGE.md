# Weather MCP Server 使用指南

## 📦 项目结构

```
weather-mcp-server/
├── weather_server.py       # MCP 服务器主程序
├── requirements.txt        # Python 依赖
├── setup.sh               # 安装脚本
├── test_weather.py        # API 测试脚本
├── direct_test.py         # 直接功能测试
├── mcp_config_example.json # Claude 配置示例
└── README.md              # 项目文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd weather-mcp-server
pip install -r requirements.txt
```

或使用安装脚本：

```bash
chmod +x setup.sh
./setup.sh
```

### 2. 测试功能

直接测试天气功能（无需 MCP）：

```bash
python3 direct_test.py
```

测试 API 连接：

```bash
python3 test_weather.py
```

### 3. 注册到 Claude

#### 方法 A: Claude Desktop

在 Claude Desktop 设置中添加以下配置：

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weather": {
      "command": "python3",
      "args": ["/完整路径/weather-mcp-server/weather_server.py"]
    }
  }
}
```

**注意:** 将 `/完整路径/` 替换为实际的项目路径，例如：
- macOS: `/Users/你的用户名/weather-mcp-server/weather_server.py`
- Linux: `/home/你的用户名/weather-mcp-server/weather_server.py`
- Windows: `C:\\Users\\你的用户名\\weather-mcp-server\\weather_server.py`

#### 方法 B: Claude Web (通过 mcp.json)

创建或编辑 `~/.claude/mcp.json`：

```bash
mkdir -p ~/.claude
cat > ~/.claude/mcp.json << EOF
{
  "mcpServers": {
    "weather": {
      "command": "python3",
      "args": ["$(pwd)/weather_server.py"]
    }
  }
}
EOF
```

### 4. 重启 Claude

配置完成后，重启 Claude Desktop 以加载 MCP 服务器。

## 🎯 使用方法

在 Claude 中，你现在可以直接询问天气相关的问题：

### 查询当前天气

```
北京的天气怎么样？
```
```
帮我查一下东京、纽约、伦敦的天气
```
```
上海现在是多少度？
```

### 查询天气预报

```
广州未来三天的天气预报
```
```
深圳明天会下雨吗？
```

### 比较天气

```
对比一下北京、上海、广州现在的天气情况
```
```
帮我看看这几个城市哪个最热：北京、上海、广州、深圳
```

## 🛠️ 可用工具

### 1. get_current_weather

获取指定城市的实时天气。

**参数：**
- `location` (string): 城市名称（支持中文和英文）

**返回：**
- `location`: 位置信息（城市、地区、国家）
- `temperature`: 温度（摄氏度/华氏度）
- `weather`: 天气状况
- `feels_like`: 体感温度
- `humidity`: 湿度百分比
- `wind`: 风速和风向
- `visibility`: 能见度
- `uv_index`: 紫外线指数

### 2. get_weather_forecast

获取指定城市的天气预报。

**参数：**
- `location` (string): 城市名称
- `days` (integer, 可选): 预报天数（1-3，默认3天）

**返回：**
- 每日最高/最低/平均温度
- 白天和夜晚天气状况
- 降雨/降雪概率

### 3. search_weather_by_city

搜索城市的详细天气数据（JSON 格式）。

**参数：**
- `city` (string): 城市名称

**返回：**
- 完整的天气数据 JSON 对象
- 包含位置、温度、湿度、风速、气压等详细信息

## 🌍 支持的城市

该服务支持全球主要城市，包括：

### 中国城市
- 北京 (Beijing)
- 上海 (Shanghai)
- 广州 (Guangzhou)
- 深圳 (Shenzhen)
- 杭州 (Hangzhou)
- 成都 (Chengdu)
- 武汉 (Wuhan)
- 西安 (Xi'an)
- 南京 (Nanjing)
- 重庆 (Chongqing)

### 国际城市
- 东京 (Tokyo)
- 纽约 (New York)
- 伦敦 (London)
- 巴黎 (Paris)
- 柏林 (Berlin)
- 悉尼 (Sydney)
- 多伦多 (Toronto)
- 迪拜 (Dubai)

## ⚠️ 注意事项

1. **API 限制**: wttr.in 是免费服务，请合理使用，避免频繁请求
2. **城市名称**: 建议使用城市英文名获得更准确的结果
3. **网络要求**: 需要能够访问 wttr.in (https://wttr.in)
4. **数据更新**: 天气数据约每小时更新一次
5. **小城市**: 部分小城市可能无法识别

## 🔧 故障排除

### 问题: Claude 无法连接到 MCP 服务器

**解决方案：**
1. 检查 Python 路径是否正确（使用 `which python3` 或 `where python3`）
2. 确认文件路径使用绝对路径
3. 检查依赖是否安装完整：`pip install -r requirements.txt`
4. 查看 Claude Desktop 日志（开发者工具）

### 问题: 无法获取天气信息

**解决方案：**
1. 测试网络连接：`curl https://wttr.in/Beijing?format=j1`
2. 尝试使用城市英文名
3. 运行测试脚本：`python3 direct_test.py`

### 问题: Windows 路径问题

**解决方案：**
- 使用双反斜杠：`C:\\Users\\...`
- 或使用正斜杠：`C:/Users/...`

## 📝 示例配置文件

### macOS/Linux

```json
{
  "mcpServers": {
    "weather": {
      "command": "python3",
      "args": ["/Users/yourname/weather-mcp-server/weather_server.py"]
    }
  }
}
```

### Windows

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["C:\\Users\\yourname\\weather-mcp-server\\weather_server.py"]
    }
  }
}
```

## 🔍 验证安装

1. 运行直接测试：
   ```bash
   python3 direct_test.py
   ```

2. 检查 Claude 是否识别工具：
   - 在 Claude 中询问："你有哪些工具可用？"
   - 应该能看到天气相关的工具

3. 测试天气查询：
   - 在 Claude 中询问："北京的天气怎么样？"

## 📚 技术细节

- **协议**: MCP (Model Context Protocol)
- **语言**: Python 3
- **SDK**: mcp >= 1.0.0
- **HTTP 客户端**: httpx
- **数据源**: wttr.in API
- **通信方式**: stdio
- **数据格式**: JSON

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 许可证

MIT License
