#!/usr/bin/env python3
"""Test script for Weather MCP Server"""

import asyncio
import httpx


async def test_weather_api():
    """Test the weather API directly"""
    print("🧪 Testing Weather API...")
    print("=" * 50)
    
    cities = ["Beijing", "Shanghai", "Tokyo", "New York"]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for city in cities:
            print(f"\n🌍 Testing {city}...")
            try:
                # Test current weather
                url = f"https://wttr.in/{city}?format=j1"
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                
                current = data.get('current_condition', [{}])[0]
                area = data.get('nearest_area', [{}])[0]
                
                temp = current.get('temp_C', 'N/A')
                condition = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
                location = area.get('areaName', [{}])[0].get('value', city)
                
                print(f"   ✅ {location}: {temp}°C, {condition}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ API Test complete!")


async def test_mcp_server():
    """Test the MCP server"""
    print("\n🧪 Testing MCP Server...")
    print("=" * 50)
    
    import subprocess
    import json
    
    # Test tools/list
    print("\n📋 Listing available tools...")
    result = subprocess.run(
        ["python3", "weather_server.py"],
        input='{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n',
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            response = json.loads(result.stdout.strip())
            if 'result' in response:
                tools = response['result'].get('tools', [])
                print(f"   ✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"      - {tool.get('name')}: {tool.get('description')}")
        except:
            print("   ⚠️  Could not parse response")
    else:
        print(f"   ❌ Server error: {result.stderr}")
    
    print("\n" + "=" * 50)
    print("✅ MCP Server Test complete!")


async def main():
    await test_weather_api()
    # MCP server test requires running the server separately
    print("\n💡 To test MCP server manually, run:")
    print("   echo '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}' | python3 weather_server.py")


if __name__ == "__main__":
    asyncio.run(main())
