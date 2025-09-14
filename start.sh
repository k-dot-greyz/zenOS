#!/bin/bash
# zenOS Quick Start Script

set -e

echo "🧘 Welcome to zenOS - AI CLI Tool"
echo "================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 No .env file found. Creating from template..."
    cp env.example .env
    echo ""
    echo "⚠️  Please edit .env and add your OpenRouter API key"
    echo "   Get your key at: https://openrouter.ai/keys"
    echo ""
    echo "   Then run this script again."
    exit 1
fi

# Check if API key is set
if grep -q "sk-or-v1-your-api-key-here" .env; then
    echo "⚠️  Please update your OpenRouter API key in .env"
    echo "   Get your key at: https://openrouter.ai/keys"
    exit 1
fi

echo "✅ Configuration looks good!"
echo ""

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting zenOS services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

echo ""
echo "✨ zenOS is ready!"
echo ""
echo "Try these commands:"
echo "  docker-compose exec zen-cli zen \"What is zenOS?\""
echo "  docker-compose exec zen-cli zen chat"
echo "  docker-compose logs -f zen-cli"
echo ""
echo "To stop zenOS:"
echo "  docker-compose down"
echo ""
echo "Enjoy the zen of AI! 🧘"
