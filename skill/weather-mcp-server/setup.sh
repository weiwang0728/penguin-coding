#!/bin/bash
# Setup script for Weather MCP Server

echo "🌦️  Setting up Weather MCP Server..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  python3 weather_server.py"
echo ""
echo "To test the server, run:"
echo "  ./test weather.sh"
echo ""
echo "To register with Claude Desktop, add to ~/.claude/mcp.json:"
echo '  "weather": {'
echo '    "command": "python3",'
echo '    "args": ["'"$(pwd)"'/weather_server.py"]'
echo '  }'
