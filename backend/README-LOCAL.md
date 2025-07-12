# AI Chatbot Backend - Local Development Guide

This guide will help you set up the AI Chatbot backend for local development without exposing any database ports.

## 🚀 Quick Start (Recommended)

### Option 1: Docker Setup (Easiest)

1. **Clone and navigate to the backend directory**
```bash
cd backend
```

2. **Run the local setup script**
```bash
chmod +x setup-local.sh
./setup-local.sh
```

3. **Edit the environment file**
```bash
# Edit .env file with your configuration
nano .env
```

4. **Access your application**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Option 2: Local Python Setup

1. **Run the local development script**
```bash
chmod +x run-local.sh
./run-local.sh
```

This will:
- Create a virtual environment
- Install dependencies
- Check prerequisites
- Start the application

## 🔧 Manual Setup

### Prerequisites

#### For Docker Setup (Option 1)
- Docker
- Docker Compose

#### For Local Python Setup (Option 2)
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Step-by-Step Manual Setup

#### 1. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file
nano .env
```

**Required environment variables:**
```bash
# Core settings
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-super-secret-key-change-in-production

# Database (for local setup)
DATABASE_URL=postgresql://postgres:password@localhost:5432/chatbot_db
REDIS_URL=redis://localhost:6379

# For Docker setup, use:
# DATABASE_URL=postgresql://postgres:password@db:5432/chatbot_db
# REDIS_URL=redis://redis:6379
```

#### 2. Docker Setup (Recommended)

```bash
# Start services (database and Redis not exposed)
docker-compose -f docker-compose.local.yml up -d

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Stop services
docker-compose -f docker-compose.local.yml down
```

#### 3. Local Python Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis locally
# (Install and start these services on your system)

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🗄️ Database Setup

### Docker Setup (Automatic)
The database is automatically created and configured when using Docker.

### Local PostgreSQL Setup

1. **Install PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

2. **Create Database**
```bash
# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql    # macOS

# Create database
createdb chatbot_db

# Or connect to PostgreSQL and create database
psql -U postgres
CREATE DATABASE chatbot_db;
\q
```

3. **Install pgvector extension**
```bash
# Connect to your database
psql -U postgres -d chatbot_db

# Install pgvector (if available)
CREATE EXTENSION IF NOT EXISTS vector;
```

### Local Redis Setup

1. **Install Redis**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows
# Download from https://redis.io/download
```

2. **Start Redis**
```bash
# Linux
sudo systemctl start redis-server

# macOS
brew services start redis

# Test connection
redis-cli ping
# Should return: PONG
```

## 🔍 Verification

### Check API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Test API Documentation
- Open http://localhost:8000/docs in your browser
- You should see the interactive Swagger documentation

## 🛠️ Development Commands

### Docker Commands
```bash
# Start services
docker-compose -f docker-compose.local.yml up -d

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Stop services
docker-compose -f docker-compose.local.yml down

# Rebuild and restart
docker-compose -f docker-compose.local.yml up --build

# Access container shell
docker-compose -f docker-compose.local.yml exec app bash
```

### Local Python Commands
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Code formatting
black app/
isort app/

# Type checking
mypy app/

# Linting
flake8 app/

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔒 Security Features

### Local Development Security
- **Database Isolation**: Database only accessible from within Docker network
- **No Exposed Ports**: PostgreSQL and Redis ports not exposed to host
- **Environment Variables**: Sensitive data stored in .env file
- **Rate Limiting**: Built-in rate limiting for API protection

### Environment File Security
```bash
# .env file should NOT be committed to version control
echo ".env" >> .gitignore

# Use .env.example for template
cp env.example .env
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -U postgres -d chatbot_db -c "SELECT 1;"
```

#### 2. Redis Connection Failed
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping
```

#### 3. Docker Services Not Starting
```bash
# Check Docker status
docker --version
docker-compose --version

# Check service logs
docker-compose -f docker-compose.local.yml logs

# Restart Docker service
sudo systemctl restart docker
```

#### 4. Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

#### 5. Python Version Issues
```bash
# Check Python version
python3 --version

# Should be 3.11 or higher
# If not, install Python 3.11+
```

### Debug Mode

Enable debug mode in `.env`:
```bash
DEBUG=true
```

This will show detailed error messages and enable auto-reload.

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Docker logs
docker-compose -f docker-compose.local.yml logs -f

# Application logs (if running locally)
# Logs will appear in the terminal where uvicorn is running
```

### Database Connection
```bash
# Check database connection from application
curl http://localhost:8000/health
# Should show database status in response
```

## 🎯 Next Steps

1. **Configure OpenAI API Key**
   - Get your API key from https://platform.openai.com/
   - Add it to your `.env` file

2. **Test the API**
   - Visit http://localhost:8000/docs
   - Try the authentication endpoints
   - Test the chat functionality

3. **Add Sample Data**
   - Create some test users
   - Add FAQ entries
   - Test the semantic search

4. **Connect Frontend**
   - Update frontend configuration to point to `http://localhost:8000`
   - Test the full application flow

## 💡 Tips

- **Hot Reload**: The application automatically reloads when you make changes
- **Database Persistence**: Data persists between Docker restarts
- **Environment Isolation**: Each service runs in its own container
- **Easy Cleanup**: `docker-compose -f docker-compose.local.yml down -v` removes all data
- **Development Mode**: Use `DEBUG=true` for detailed error messages

## 🔗 Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Documentation](https://docs.docker.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

Your local development environment is now ready! The database and Redis are secure and isolated within the Docker network, and you can develop without exposing any sensitive services to your local machine. 