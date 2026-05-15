# Weather MCP Server

一个基于 wttr.in API 的天气 MCP (Model Context Protocol) 服务器，为 Claude 提供天气查询功能。

## 功能特性

- ✨ 获取实时天气信息
- 🔮 获取天气预报（最多3天）
- 🔍 按城市搜索详细天气数据
- 🌍 支持全球城市
- 🆓 无需 API 密钥（使用免费 wttr.in 服务）
- 🇨🇳 中文输出

## 安装

### 1. 创建虚拟环境

```bash
cd weather-mcp-server
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 注册到 Claude

编辑 `~/.claude/mcp.json`（或通过 Claude Desktop 设置）：

```json
{
  "mcpServers": {
    "weather": {
      "command": "python3",
      "args": ["/root/my-cluade-code/skill/weather-mcp-server/weather_server.py"]
    }
  }
}
```

### Claude Desktop 设置

在 Claude Desktop 的设置中添加：

```json
{
  "mcpServers": {
    "weather": {
      "command": "python3",
      "args": ["/path/to/weather-mcp-server/weather_server.py"]
    }
  }
}
```

## 可用工具

### 1. get_current_weather

获取指定城市的实时天气。

**参数：**
- `location` (string): 城市名称（如 "Beijing", "Shanghai", "New York"）

**示例：**
```
获取北京的当前天气
```

### 2. get_weather_forecast

获取指定城市的天气预报。

**参数：**
- `location` (string): 城市名称
- `days` (integer, 可选): 预报天数（1-3天，默认3天）

**示例：**
```
获取上海未来3天的天气预报
```

### 3. search_weather_by_city

搜索城市的详细天气数据（JSON格式）。

**参数：**
- `city` (string): 城市名称

**示例：**
```
搜索深圳的详细天气信息
```

## 使用示例

在 Claude 中你可以这样询问：

```
北京的天气怎么样？
```
```
帮我查一下上海和东京的当前天气
```
```
广州未来两天的天气预报是什么？
```
```
对比一下北京、上海、广州的天气情况
```

## 测试

### 使用 MCP Inspector 测试

```bash
npx @anthropics/mcp-inspector python3 weather_server.py
```

### 手动测试

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 weather_server.py
```

## 技术说明

- 使用 **wttr.in** 免费天气 API
- 基于 Python MCP SDK 构建
- 异步 HTTP 请求，性能高效
- 支持中英文城市名称

## 支持的城市示例

- 中国城市：北京、上海、广州、深圳、杭州、成都、武汉等
- 国际城市：Tokyo、New York、London、Paris、Berlin、Sydney 等
- 支持城市中文名和英文名

## 注意事项

1. wttr.in 是免费服务，可能有请求频率限制
2. 某些小城市可能无法识别
3. 天气数据更新频率约为每小时一次
4. 建议使用城市英文名获得更准确的结果

## 故障排除

**问题：无法获取天气信息**
- 检查网络连接
- 确认城市名称拼写正确
- 尝试使用城市英文名

**问题：MCP 服务器无法连接**
- 确认 Python 路径正确
- 检查依赖是否安装完整
- 查看 Claude Desktop 日志

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
