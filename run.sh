#!/bin/bash

# Advanced Pterodactyl Backup Bot - Run Script
# For Linux/macOS systems

echo "========================================="
echo "   Advanced Pterodactyl Backup Bot"
echo "========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found!${NC}"
    echo "Please install Python 3.7+ first."
    echo "On Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "On macOS: brew install python3"
    exit 1
fi

echo -e "${GREEN}✅ Python3 found:${NC} $(python3 --version)"

# Check config
if [ ! -f "config.py" ]; then
    echo -e "${RED}❌ config.py not found!${NC}"
    echo "Please make sure config.py exists and is configured properly."
    echo
    echo "Run 'python3 setup.py' first to validate your setup."
    exit 1
fi

echo -e "${GREEN}✅ Configuration file found${NC}"

# Install requirements if needed (first time setup)
if [ ! -f "bot_data.json" ]; then
    echo -e "${YELLOW}📦 First time setup - Installing requirements...${NC}"
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install requirements!${NC}"
        echo "Please run 'python3 setup.py' for troubleshooting."
        exit 1
    fi
    echo -e "${GREEN}✅ Requirements installed successfully!${NC}"
    echo
fi

echo -e "${BLUE}🚀 Starting Advanced Pterodactyl Backup Bot...${NC}"
echo -e "${BLUE}⏰ Started at:${NC} $(date)"
echo -e "${BLUE}📁 Working directory:${NC} $(pwd)"
echo

# Run the bot
python3 main.py
exit_code=$?

# Handle exit status
if [ $exit_code -ne 0 ]; then
    echo
    echo -e "${RED}❌ Bot stopped with error code: $exit_code${NC}"
    echo -e "${YELLOW}📞 For troubleshooting, check:${NC}"
    echo "   • bot_backup.log file for detailed logs"
    echo "   • Your internet connection"
    echo "   • API keys in config.py"
    echo "   • Pterodactyl panel accessibility"
else
    echo
    echo -e "${GREEN}✅ Bot stopped normally.${NC}"
fi

echo
echo -e "${BLUE}📊 Bot session ended at:${NC} $(date)"