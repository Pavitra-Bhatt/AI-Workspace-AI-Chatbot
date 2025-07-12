# AI Chatbot Backend

A production-ready FastAPI backend for an AI-powered chatbot system with GPT-4 integration, real-time messaging, and comprehensive analytics.

## 🏗️ Architecture Overview

### Technology Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with async SQLAlchemy
- **Cache**: Redis for session management and caching
- **AI**: OpenAI GPT-4 Turbo with embeddings
- **Authentication**: JWT with refresh tokens
- **Real-time**: WebSocket support
- **Monitoring**: Structured logging with structlog
- **Rate Limiting**: SlowAPI for request throttling

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Mobile App    │    │   Admin Panel   │
│   (React)       │    │   (React Native)│    │   (React)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI API   │
                    │   (Backend)     │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   OpenAI API    │
│   (Database)    │    │   (Cache/Queue) │    │   (AI Service)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development

1. **Clone and setup**
```bash
cd backend
cp env.example .env
# Edit .env with your configuration
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run with Docker Compose**
```bash
docker-compose up -d
```

4. **Run migrations**
```bash
alembic upgrade head
```

5. **Start the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📊 Database Schema

### Core Tables

#### Users
- User authentication and profile management
- GDPR compliance tracking
- Role-based access control

#### Conversations
- Chat session management
- Message history and context
- Analytics tracking

#### Messages
- Individual message storage
- AI response tracking
- Token usage monitoring

#### FAQs
- Knowledge base management
- Vector embeddings for semantic search
- Multi-language support

#### Analytics
- User behavior tracking
- Conversation metrics
- Performance monitoring

#### Audit Logs
- GDPR compliance
- Security event tracking
- Data access logging

## 🔐 Authentication & Security

### JWT Authentication
- Access tokens (30 minutes)
- Refresh tokens (7 days)
- Secure token validation

### Rate Limiting
- Per-minute limits: 60 requests
- Per-hour limits: 1000 requests
- IP-based throttling

### Security Features
- CORS protection
- Input validation
- SQL injection prevention
- XSS protection
- Audit logging

## 🤖 AI Integration

### OpenAI GPT-4
- Real-time conversation processing
- Context-aware responses
- Token usage optimization

### Semantic Search
- Vector embeddings for FAQ search
- Cosine similarity matching
- Multi-language support

### Content Moderation
- OpenAI moderation API
- Inappropriate content filtering
- Safety compliance

## 📈 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout

### Chat
- `POST /api/v1/chat/send` - Send message
- `WS /api/v1/chat/ws/{user_id}` - WebSocket chat

### Conversations
- `GET /api/v1/conversations` - List conversations
- `GET /api/v1/conversations/{id}` - Get conversation
- `DELETE /api/v1/conversations/{id}` - Delete conversation

### FAQ Management
- `GET /api/v1/faqs` - List FAQs
- `POST /api/v1/faqs` - Create FAQ
- `PUT /api/v1/faqs/{id}` - Update FAQ
- `GET /api/v1/faqs/search` - Search FAQs

### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard metrics
- `GET /api/v1/analytics/user/{id}` - User analytics
- `GET /api/v1/analytics/conversations` - Conversation analytics

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `SECRET_KEY` | JWT secret key | - |
| `DEBUG` | Debug mode | `false` |

### Database Configuration
```python
DATABASE_URL=postgresql://user:password@localhost/chatbot_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

### Redis Configuration
```python
REDIS_URL=redis://localhost:6379
REDIS_DB=0
```

## 🧪 Testing

### Run Tests
```bash
pytest tests/
```

### Test Coverage
```bash
pytest --cov=app tests/
```

## 📊 Monitoring & Logging

### Structured Logging
- JSON-formatted logs
- Request/response tracking
- Error monitoring
- Performance metrics

### Health Checks
- Database connectivity
- Redis connectivity
- OpenAI API status
- Application health

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t chatbot-backend .
docker run -p 8000:8000 chatbot-backend
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatbot-backend
  template:
    metadata:
      labels:
        app: chatbot-backend
    spec:
      containers:
      - name: chatbot-backend
        image: chatbot-backend:latest
        ports:
        - containerPort: 8000
```

## 🔒 Security Considerations

### GDPR Compliance
- Data retention policies
- User consent tracking
- Data export capabilities
- Right to be forgotten

### OWASP Compliance
- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection
- Rate limiting

## 📈 Performance Optimization

### Caching Strategy
- Redis for session storage
- Response caching
- FAQ embedding cache
- User analytics cache

### Database Optimization
- Connection pooling
- Indexed queries
- Async operations
- Query optimization

### AI Response Optimization
- Token usage monitoring
- Response time tracking
- Fallback mechanisms
- Error handling

## 🔄 Background Jobs

### Celery Tasks
- Email notifications
- Analytics processing
- Data cleanup
- Report generation

### Scheduled Tasks
- Data retention cleanup
- Analytics aggregation
- System health checks
- Performance monitoring

## 📚 API Documentation

### Interactive Documentation
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI 3.0 specification

### Example Requests

#### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

#### Send Chat Message
```bash
curl -X POST "http://localhost:8000/api/v1/chat/send" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how can you help me?",
    "language": "en"
  }'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`

## 🔄 Changelog

### Version 1.0.0
- Initial release
- FastAPI backend with GPT-4 integration
- Real-time WebSocket support
- Comprehensive analytics
- GDPR compliance features 