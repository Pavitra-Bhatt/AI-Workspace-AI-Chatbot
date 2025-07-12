# AI Chatbot Backend

A production-ready AI chatbot backend built with FastAPI, featuring real-time messaging, AI integration, FAQ system, and comprehensive admin capabilities.

## 🚀 Tech Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs with Python
- **SQLAlchemy** - SQL toolkit and ORM for database operations
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type annotations

### Database & Caching
- **PostgreSQL** - Primary database (production)
- **SQLite** - Local development database
- **Redis** - Caching and session storage

### Authentication & Security
- **JWT** - JSON Web Tokens for authentication
- **bcrypt** - Password hashing
- **CORS** - Cross-Origin Resource Sharing
- **Rate Limiting** - API abuse prevention

### AI & Machine Learning
- **OpenAI GPT-4 Turbo** - Primary AI model (paid tier)
- **HuggingFace Transformers** - Local AI models (free tier)
- **sentence-transformers** - Semantic search embeddings
- **Local Models** - Offline AI capabilities

### Real-time Communication
- **WebSockets** - Real-time messaging
- **FastAPI WebSocket** - WebSocket support

### Development & Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async testing support
- **Postman** - API testing and documentation
- **Docker** - Containerization

### Monitoring & Logging
- **structlog** - Structured logging
- **Prometheus** - Metrics and monitoring
- **Health Checks** - Application health monitoring

## 🏗️ Architecture

### Project Structure
```
backend/
├── app/
│   ├── api/           # API routes and endpoints
│   │   ├── auth.py    # Authentication endpoints
│   │   ├── chat.py    # Chat and messaging endpoints
│   │   ├── faq.py     # FAQ management endpoints
│   │   ├── admin.py   # Admin dashboard endpoints
│   │   └── system.py  # System health endpoints
│   ├── auth/          # Authentication and authorization
│   │   ├── jwt.py     # JWT token management
│   │   └── security.py # Security utilities
│   ├── models/        # SQLAlchemy database models
│   │   ├── user.py    # User model
│   │   ├── chat.py    # Chat and message models
│   │   ├── faq.py     # FAQ models
│   │   └── analytics.py # Analytics models
│   ├── schemas/       # Pydantic schemas for validation
│   │   ├── auth.py    # Authentication schemas
│   │   ├── chat.py    # Chat schemas
│   │   ├── faq.py     # FAQ schemas
│   │   └── user.py    # User schemas
│   ├── services/      # Business logic and external integrations
│   │   ├── ai_service.py      # AI model integration
│   │   ├── faq_service.py     # FAQ management
│   │   ├── notification_service.py # Email notifications
│   │   └── analytics_service.py # Analytics tracking
│   ├── config.py      # Application configuration
│   ├── database.py    # Database connection and session management
│   └── main.py        # FastAPI application entry point
├── requirements.txt   # Python dependencies
├── docker-compose.yml # Docker orchestration
└── README.md         # Project documentation
```

### Database Design
- **User** - User accounts and authentication
- **Conversation** - Chat conversations
- **Message** - Individual chat messages
- **FAQ** - Frequently asked questions
- **FAQCategory** - FAQ categorization
- **Analytics** - User behavior tracking
- **AuditLog** - GDPR compliance logging

### API Design
- **RESTful API** with FastAPI
- **WebSocket endpoints** for real-time chat
- **JWT authentication** for secure access
- **Rate limiting** to prevent abuse
- **CORS middleware** for frontend integration

## 🤖 AI Integration

### AI Service Architecture
- **Multi-provider support** (OpenAI, HuggingFace, Local)
- **Fallback mechanisms** for AI failures
- **Local models** for free tier usage
- **Embedding generation** for semantic search
- **Content moderation** with keyword filtering

### FAQ System
- **Semantic search** using vector embeddings
- **Text-based search** as fallback
- **Category-based organization**
- **Priority and status management**
- **Analytics tracking** for FAQ usage

### Chat Features
- **Conversation history** management
- **Message threading** and context
- **Real-time WebSocket** communication
- **Message status** tracking (sent, delivered, read)
- **Token usage** tracking for AI responses

## 🔧 Development Process

### AI Tools Used Throughout Development

#### 1. **Cursor AI Assistant**
- **Primary Development Partner**: Used throughout the entire project development
- **Code Generation**: Generated initial project structure, models, and services
- **Bug Fixing**: Resolved dependency conflicts, import errors, and syntax issues
- **Architecture Design**: Helped design the overall system architecture
- **Best Practices**: Ensured code follows FastAPI and Python best practices

#### 2. **Code Analysis & Debugging**
- **Error Resolution**: Fixed multiple issues including:
  - Dependency conflicts between `googletrans` and `httpx`
  - Missing `Enum` imports in SQLAlchemy models
  - Reserved attribute name `metadata` conflicts
  - Module import errors and circular imports
  - Syntax errors in f-strings
  - Database connection issues

#### 3. **Configuration Management**
- **Environment Setup**: Created comprehensive `.env` files
- **Dependency Management**: Resolved version conflicts in `requirements.txt`
- **Database Configuration**: Switched between PostgreSQL and SQLite for different environments

#### 4. **API Development**
- **Endpoint Creation**: Built all REST API endpoints
- **WebSocket Implementation**: Real-time chat functionality
- **Authentication System**: JWT-based auth with bcrypt password hashing
- **Validation**: Pydantic schemas for request/response validation

#### 5. **Testing & Documentation**
- **Postman Collection**: Created comprehensive API testing collection
- **Error Handling**: Implemented proper error responses
- **Documentation**: Generated inline documentation and comments

### Key Development Challenges Solved

1. **Dependency Management**
   - Resolved conflicts between `googletrans` and `httpx`
   - Fixed version incompatibilities between `openai` and `httpx`
   - Installed missing packages like `bcrypt` and `aiosmtplib`

2. **Database Issues**
   - Fixed SQLAlchemy relationship warnings
   - Resolved circular import issues
   - Configured both PostgreSQL and SQLite support

3. **AI Service Integration**
   - Implemented fallback mechanisms for AI failures
   - Created local model support for free tier
   - Built semantic search capabilities

4. **Authentication & Security**
   - Implemented JWT token management
   - Added bcrypt password hashing
   - Configured CORS and rate limiting

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-workshop
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   # For SQLite (local development)
   python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

5. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Environment Configuration

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./chatbot.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration
AI_PROVIDER=local  # or openai
OPENAI_API_KEY=your-openai-key  # if using OpenAI

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh

### Chat Endpoints
- `GET /api/v1/chat/conversations` - Get user conversations
- `POST /api/v1/chat/conversations` - Create new conversation
- `GET /api/v1/chat/conversations/{id}/messages` - Get conversation messages
- `POST /api/v1/chat/conversations/{id}/messages` - Send message
- `WebSocket /ws/chat/{conversation_id}` - Real-time chat

### FAQ Endpoints
- `GET /api/v1/faq/search` - Search FAQs
- `GET /api/v1/faq/categories` - Get FAQ categories
- `POST /api/v1/faq/` - Create FAQ (admin)
- `PUT /api/v1/faq/{id}` - Update FAQ (admin)

### Admin Endpoints
- `GET /api/v1/admin/users` - Get all users
- `GET /api/v1/admin/analytics` - Get analytics data
- `POST /api/v1/admin/users/{id}/status` - Update user status

## 🧪 Testing

### Using Postman
1. Import the provided `AI_Chatbot_API.postman_collection.json`
2. Set up environment variables in Postman
3. Test all endpoints systematically

### Manual Testing
```bash
# Test registration
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Test login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

## 🔒 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - bcrypt for secure password storage
- **Rate Limiting** - Prevents API abuse
- **CORS Protection** - Secure cross-origin requests
- **Input Validation** - Pydantic schema validation
- **SQL Injection Prevention** - SQLAlchemy ORM protection
- **Audit Logging** - GDPR compliance tracking

## 📊 Monitoring & Analytics

- **Health Checks** - Application health monitoring
- **Structured Logging** - Comprehensive logging with context
- **Performance Metrics** - Response time tracking
- **Error Tracking** - Exception monitoring and alerting
- **User Analytics** - Behavior tracking and insights

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Production Considerations
- Use PostgreSQL for production database
- Configure Redis for caching and sessions
- Set up proper environment variables
- Enable HTTPS with SSL certificates
- Configure monitoring and alerting
- Set up automated backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI** team for the excellent web framework
- **SQLAlchemy** team for the powerful ORM
- **OpenAI** for AI model integration
- **HuggingFace** for local model support
- **Cursor AI** for development assistance throughout the project

---

**Note**: This project is designed to work with free-tier services and local models, making it accessible for developers without expensive API costs while maintaining production-ready quality. 