#!/usr/bin/env python3
"""weather_server.py - A weather MCP server using wttr.in API"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx
import json

# Create server instance
server = Server("weather-server")

# Define tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'Beijing', 'Shanghai', 'New York')"
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="get_weather_forecast",
            description="Get weather forecast for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'Beijing', 'Shanghai', 'New York')"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast (1-3, default 3)",
                        "minimum": 1,
                        "maximum": 3,
                        "default": 3
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="search_weather_by_city",
            description="Search for weather information by city name and return detailed JSON data",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name to search"
                    }
                },
                "required": ["city"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "get_current_weather":
        location = arguments.get("location")
        result = await get_current_weather(location)
        return [TextContent(type="text", text=result)]
    
    elif name == "get_weather_forecast":
        location = arguments.get("location")
        days = arguments.get("days", 3)
        result = await get_weather_forecast(location, days)
        return [TextContent(type="text", text=result)]
    
    elif name == "search_weather_by_city":
        city = arguments.get("city")
        result = await search_weather_by_city(city)
        return [TextContent(type="text", text=result)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def get_current_weather(location: str) -> str:
    """Get current weather for a location"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://wttr.in/{location}?format=j1"
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            current = data.get('current_condition', [{}])[0]
            temp_c = current.get('temp_C', 'N/A')
            temp_f = current.get('temp_F', 'N/A')
            humidity = current.get('humidity', 'N/A')
            wind_kph = current.get('windspeedKmph', 'N/A')
            wind_dir = current.get('winddir16Point', 'N/A')
            condition = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
            feels_like_c = current.get('FeelsLikeC', 'N/A')
            uv_index = current.get('uvIndex', 'N/A')
            visibility = current.get('visibility', 'N/A')
            
            nearest_area = data.get('nearest_area', [{}])[0]
            area_name = nearest_area.get('areaName', [{}])[0].get('value', location)
            country = nearest_area.get('country', [{}])[0].get('value', 'N/A')
            region = nearest_area.get('region', [{}])[0].get('value', 'N/A')
            
            result = f"""🌍 位置: {area_name}, {region}, {country}
🌡️  温度: {temp_c}°C ({temp_f}°F)
🌤️  天气: {condition}
🤔  体感: {feels_like_c}°C
💧  湿度: {humidity}%
💨  风速: {wind_kph} km/h {wind_dir}
👁️  能见度: {visibility} km
☀️  紫外线指数: {uv_index}"""
            
            return result
            
    except httpx.TimeoutException:
        return "❌ 错误: 请求超时，请稍后重试"
    except httpx.HTTPError as e:
        return f"❌ HTTP错误: {str(e)}"
    except Exception as e:
        return f"❌ 错误: {str(e)}。请检查城市名称是否正确。"


async def get_weather_forecast(location: str, days: int = 3) -> str:
    """Get weather forecast for a location"""
    try:
        days = min(max(days, 1), 3)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://wttr.in/{location}?format=j1&n={days}"
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            nearest_area = data.get('nearest_area', [{}])[0]
            area_name = nearest_area.get('areaName', [{}])[0].get('value', location)
            country = nearest_area.get('country', [{}])[0].get('value', 'N/A')
            
            forecast_list = data.get('weather', [])
            
            result = f"📍 {area_name}, {country} - 未来 {days} 天天气预报\n\n"
            
            for day_data in forecast_list[:days]:
                date = day_data.get('date', 'N/A')
                avg_temp = day_data.get('avgtempC', 'N/A')
                max_temp = day_data.get('maxtempC', 'N/A')
                min_temp = day_data.get('mintempC', 'N/A')
                
                hourly = day_data.get('hourly', [])
                if len(hourly) >= 2:
                    day_condition = hourly[0].get('weatherDesc', [{}])[0].get('value', 'N/A')
                    day_chance_of_rain = hourly[0].get('chanceofrain', '0')
                    day_chance_of_snow = hourly[0].get('chanceofsnow', '0')
                    night_condition = hourly[2].get('weatherDesc', [{}])[0].get('value', 'N/A')
                else:
                    day_condition = "N/A"
                    night_condition = "N/A"
                    day_chance_of_rain = "0"
                    day_chance_of_snow = "0"
                
                result += f"📅 {date}\n"
                result += f"   🌡️  温度: {min_temp}°C ~ {max_temp}°C (平均 {avg_temp}°C)\n"
                result += f"   ☀️  白天: {day_condition} (降雨概率: {day_chance_of_rain}%, 降雪概率: {day_chance_of_snow}%)\n"
                result += f"   🌙  夜晚: {night_condition}\n\n"
            
            return result
            
    except httpx.TimeoutException:
        return "❌ 错误: 请求超时，请稍后重试"
    except httpx.HTTPError as e:
        return f"❌ HTTP错误: {str(e)}"
    except Exception as e:
        return f"❌ 错误: {str(e)}。请检查城市名称是否正确。"


async def search_weather_by_city(city: str) -> str:
    """Search for weather information by city name"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://wttr.in/{city}?format=j1"
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            current = data.get('current_condition', [{}])[0]
            nearest_area = data.get('nearest_area', [{}])[0]
            
            result = {
                "location": {
                    "name": nearest_area.get('areaName', [{}])[0].get('value', city),
                    "region": nearest_area.get('region', [{}])[0].get('value', 'N/A'),
                    "country": nearest_area.get('country', [{}])[0].get('value', 'N/A'),
                    "latitude": nearest_area.get('lat', 'N/A'),
                    "longitude": nearest_area.get('lon', 'N/A'),
                },
                "current_weather": {
                    "temperature_celsius": float(current.get('temp_C', 0)),
                    "temperature_fahrenheit": float(current.get('temp_F', 0)),
                    "feels_like_celsius": float(current.get('FeelsLikeC', 0)),
                    "condition": current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                    "humidity_percent": int(current.get('humidity', 0)),
                    "wind_speed_kmh": float(current.get('windspeedKmph', 0)),
                    "wind_direction": current.get('winddir16Point', 'N/A'),
                    "wind_degree": int(current.get('winddirDegree', 0)),
                    "visibility_km": float(current.get('visibility', 0)),
                    "uv_index": int(current.get('uvIndex', 0)),
                    "pressure_mb": int(current.get('pressure', 0)),
                    "cloudcover_percent": int(current.get('cloudcover', 0)),
                }
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# Run server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
