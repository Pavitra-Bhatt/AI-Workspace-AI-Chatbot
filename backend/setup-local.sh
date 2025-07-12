#!/bin/bash

# AI Chatbot Backend - Local Setup Script
echo "🚀 Setting up AI Chatbot Backend for local development..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
    echo "   - Add your OpenAI API key"
    echo "   - Update SECRET_KEY for production"
    echo "   - Configure other settings as needed"
else
    echo "✅ .env file already exists"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "🐳 Starting services with Docker Compose (local only)..."
docker-compose -f docker-compose.local.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
if docker-compose -f docker-compose.local.yml ps | grep -q "Up"; then
    echo "✅ All services are running!"
else
    echo "❌ Some services failed to start. Check logs with:"
    echo "   docker-compose -f docker-compose.local.yml logs"
    exit 1
fi

echo ""
echo "🎉 Setup complete! Your AI Chatbot Backend is ready."
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your OpenAI API key"
echo "   2. Access the API at: http://localhost:8000"
echo "   3. View API docs at: http://localhost:8000/docs"
echo "   4. View ReDoc at: http://localhost:8000/redoc"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: docker-compose -f docker-compose.local.yml logs -f"
echo "   - Stop services: docker-compose -f docker-compose.local.yml down"
echo "   - Restart services: docker-compose -f docker-compose.local.yml restart"
echo "   - Rebuild: docker-compose -f docker-compose.local.yml up --build"
echo ""
echo "💡 The database and Redis are only accessible from within the Docker network."
echo "   This keeps your local setup secure and isolated." 