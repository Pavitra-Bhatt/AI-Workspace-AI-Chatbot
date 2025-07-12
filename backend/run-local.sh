#!/bin/bash

# AI Chatbot Backend - Local Development (No Docker)
echo "🚀 Starting AI Chatbot Backend for local development..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
    echo "   - Add your OpenAI API key"
    echo "   - Update database and Redis URLs for local services"
    echo "   - Update SECRET_KEY for production"
else
    echo "✅ .env file already exists"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python version $PYTHON_VERSION is too old. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🔧 Prerequisites:"
echo "   Make sure you have PostgreSQL and Redis running locally, or update .env to use:"
echo "   - DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db"
echo "   - REDIS_URL=redis://localhost:6379"
echo ""
echo "   You can install them with:"
echo "   - PostgreSQL: https://www.postgresql.org/download/"
echo "   - Redis: https://redis.io/download"
echo ""

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL connection..."
if command -v psql &> /dev/null; then
    if psql -h localhost -U postgres -d chatbot_db -c "SELECT 1;" &> /dev/null 2>&1; then
        echo "✅ PostgreSQL is running and accessible"
    else
        echo "⚠️  PostgreSQL connection failed. Make sure PostgreSQL is running and accessible."
        echo "   You may need to:"
        echo "   1. Start PostgreSQL service"
        echo "   2. Create database: createdb chatbot_db"
        echo "   3. Update .env with correct credentials"
    fi
else
    echo "⚠️  psql not found. Please install PostgreSQL client tools."
fi

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null 2>&1; then
        echo "✅ Redis is running and accessible"
    else
        echo "⚠️  Redis connection failed. Make sure Redis is running."
        echo "   You may need to start Redis service."
    fi
else
    echo "⚠️  redis-cli not found. Please install Redis client tools."
fi

echo ""
echo "🚀 Starting FastAPI application..."
echo "   The API will be available at: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   ReDoc: http://localhost:8000/redoc"
echo ""
echo "💡 Press Ctrl+C to stop the application"
echo ""

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 