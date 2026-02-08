#!/bin/bash

# Ngenda Hotel Production Deployment Script
# Usage: ./deploy-production.sh

set -e  # Exit on any error

echo "🚀 Starting Ngenda Hotel Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}❌ Error: .env.production file not found!${NC}"
    echo "Please copy .env.production to .env and update with production values"
    exit 1
fi

# Copy production environment
echo -e "${YELLOW}📋 Setting up production environment...${NC}"
cp .env.production .env

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Error: Virtual environment not found!${NC}"
    echo "Please run: python3 -m venv venv"
    echo "Then run: source venv/bin/activate"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🐍 Activating Python virtual environment...${NC}"
source venv/bin/activate

# Install/update dependencies
echo -e "${YELLOW}📦 Installing/updating dependencies...${NC}"
pip install -r requirements.txt

# Check if Gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}🔧 Installing Gunicorn...${NC}"
    pip install gunicorn
fi

# Run production checks
echo -e "${YELLOW}🔍 Running production checks...${NC}"

# Check HMS API connectivity
echo "Checking HMS API connectivity..."
if curl -s --max-time 10 "${HMS_API_URL:-https://api.ngendahotel.com}/api/public/rooms" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ HMS API is accessible${NC}"
else
    echo -e "${YELLOW}⚠️  HMS API not accessible, will use fallback rooms${NC}"
fi

# Check configuration
echo "Checking configuration..."
python3 -c "
import os
from config import config
print('✅ Configuration loaded successfully')
print(f'Environment: {os.getenv(\"FLASK_ENV\", \"development\")}')
print(f'HMS API URL: {os.getenv(\"HMS_API_URL\", \"Not set\")}')
print(f'Debug Mode: {os.getenv(\"FLASK_DEBUG\", \"False\")}')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Configuration check passed${NC}"
else
    echo -e "${RED}❌ Configuration check failed${NC}"
    exit 1
fi

# Create logs directory
echo -e "${YELLOW}📁 Setting up logs directory...${NC}"
mkdir -p logs

# Start the application
echo -e "${GREEN}🚀 Starting Ngenda Hotel production server...${NC}"
echo "Server will be available at: http://0.0.0.0:5002"
echo "Press Ctrl+C to stop the server"
echo ""

# Start with Gunicorn
exec gunicorn \
    --bind 0.0.0.0:5002 \
    --workers 4 \
    --worker-class sync \
    --worker-connections 1000 \
    --timeout 120 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --capture-output \
    app:app
