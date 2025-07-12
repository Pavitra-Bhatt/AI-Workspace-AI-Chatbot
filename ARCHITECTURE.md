# AI Chatbot System Architecture

## 🏗️ System Overview

This document provides a comprehensive overview of the AI Chatbot system architecture, including design decisions, technology choices, and implementation details.

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Database Design](#database-design)
4. [API Design](#api-design)
5. [Security Architecture](#security-architecture)
6. [AI Integration](#ai-integration)
7. [Performance Considerations](#performance-considerations)
8. [Scalability Strategy](#scalability-strategy)
9. [Deployment Architecture](#deployment-architecture)
10. [Monitoring & Observability](#monitoring--observability)

## 🏛️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Web App (React)  │  Mobile App (RN)  │  Admin Panel (React) │
└────────────────────┼────────────────────┼──────────────────────┘
                     │
         ┌─────────────────────────────────┐
         │         API Gateway            │
         │     (Rate Limiting, CORS)     │
         └─────────────────────────────────┘
                     │
         ┌─────────────────────────────────┐
         │      FastAPI Application       │
         │   (Authentication, Business    │
         │    Logic, Request Handling)    │
         └─────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌─────────┐    ┌─────────┐    ┌─────────┐
│PostgreSQL│    │  Redis  │    │ OpenAI  │
│Database │    │  Cache  │    │   API   │
└─────────┘    └─────────┘    └─────────┘
```

### Component Architecture

#### 1. API Gateway Layer
- **Rate Limiting**: Per-user and per-IP request throttling
- **CORS Management**: Cross-origin resource sharing
- **Request Validation**: Input sanitization and validation
- **Authentication**: JWT token validation

#### 2. Application Layer
- **FastAPI Framework**: High-performance async web framework
- **Dependency Injection**: Clean separation of concerns
- **Middleware Stack**: Logging, error handling, monitoring
- **WebSocket Support**: Real-time communication

#### 3. Service Layer
- **AI Service**: OpenAI GPT-4 integration
- **FAQ Service**: Knowledge base management
- **Analytics Service**: User behavior tracking
- **Notification Service**: Email and push notifications

#### 4. Data Layer
- **PostgreSQL**: Primary database with async support
- **Redis**: Caching and session management
- **Vector Storage**: Embeddings for semantic search

## 🛠️ Technology Stack

### Backend Framework
**FastAPI** was chosen over Django for the following reasons:

#### Advantages of FastAPI:
- **Performance**: Native async/await support for high concurrency
- **Type Safety**: Built-in Pydantic validation
- **Auto Documentation**: Automatic OpenAPI/Swagger generation
- **Modern Python**: Latest Python features and best practices
- **WebSocket Support**: Native WebSocket handling
- **Lightweight**: Minimal overhead compared to Django

#### Why not Django:
- **Synchronous by default**: Django's ORM is synchronous
- **Heavy framework**: More overhead than needed for API
- **Complex async**: Requires additional setup for async operations

### Database Choice
**PostgreSQL** with **pgvector** extension:

#### Advantages:
- **ACID Compliance**: Full transaction support
- **Vector Support**: Native vector operations with pgvector
- **JSON Support**: Native JSONB for flexible data storage
- **Performance**: Excellent query optimization
- **Scalability**: Horizontal and vertical scaling options

#### Alternative Considered:
- **MongoDB**: Rejected due to lack of vector support and ACID compliance

### Caching Strategy
**Redis** for multiple purposes:

#### Use Cases:
- **Session Storage**: User session management
- **Response Caching**: API response caching
- **Rate Limiting**: Request throttling storage
- **Queue Management**: Background job queues
- **Real-time Data**: WebSocket connection state

## 🗄️ Database Design

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role user_role DEFAULT 'user',
    status user_status DEFAULT 'active',
    avatar_url VARCHAR(500),
    language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    gdpr_consent BOOLEAN DEFAULT FALSE,
    data_processing_consent BOOLEAN DEFAULT FALSE,
    marketing_consent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);
```

#### Conversations Table
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    context JSONB,
    tags JSONB,
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    duration_seconds INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_message_at TIMESTAMP WITH TIME ZONE
);
```

#### Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    message_type message_type NOT NULL,
    status message_status DEFAULT 'sent',
    tokens_used INTEGER DEFAULT 0,
    model_used VARCHAR(100),
    response_time_ms INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE
);
```

#### FAQs Table with Vector Support
```sql
CREATE TABLE faqs (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES faq_categories(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords JSONB,
    question_embedding vector(1536),  -- OpenAI embedding dimension
    answer_embedding vector(1536),
    status faq_status DEFAULT 'draft',
    priority INTEGER DEFAULT 0,
    language VARCHAR(10) DEFAULT 'en',
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    slug VARCHAR(255) UNIQUE,
    meta_title VARCHAR(255),
    meta_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE
);

-- Create vector indexes for semantic search
CREATE INDEX faqs_question_embedding_idx ON faqs USING ivfflat (question_embedding vector_cosine_ops);
CREATE INDEX faqs_answer_embedding_idx ON faqs USING ivfflat (answer_embedding vector_cosine_ops);
```

### Indexing Strategy

#### Performance Indexes
```sql
-- User authentication
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Conversation queries
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- Message queries
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- FAQ search
CREATE INDEX idx_faqs_status_language ON faqs(status, language);
CREATE INDEX idx_faqs_category_id ON faqs(category_id);
```

## 🔌 API Design

### RESTful API Structure

#### Authentication Endpoints
```
POST   /api/v1/auth/register     # User registration
POST   /api/v1/auth/login        # User login
POST   /api/v1/auth/refresh      # Token refresh
POST   /api/v1/auth/logout       # User logout
```

#### Chat Endpoints
```
POST   /api/v1/chat/send         # Send message
WS     /api/v1/chat/ws/{user_id} # WebSocket connection
```

#### Conversation Management
```
GET    /api/v1/conversations     # List conversations
GET    /api/v1/conversations/{id} # Get conversation
PUT    /api/v1/conversations/{id} # Update conversation
DELETE /api/v1/conversations/{id} # Delete conversation
```

#### FAQ Management
```
GET    /api/v1/faqs              # List FAQs
POST   /api/v1/faqs              # Create FAQ
GET    /api/v1/faqs/{id}         # Get FAQ
PUT    /api/v1/faqs/{id}         # Update FAQ
DELETE /api/v1/faqs/{id}         # Delete FAQ
GET    /api/v1/faqs/search       # Search FAQs
```

#### Analytics Endpoints
```
GET    /api/v1/analytics/dashboard    # Dashboard metrics
GET    /api/v1/analytics/user/{id}    # User analytics
GET    /api/v1/analytics/conversations # Conversation analytics
```

### WebSocket API

#### Connection
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/v1/chat/ws/${userId}`);
```

#### Message Format
```json
{
  "type": "message",
  "content": "Hello, how can you help me?",
  "conversation_id": 123,
  "language": "en"
}
```

#### Response Format
```json
{
  "type": "response",
  "content": "Hello! I'm here to help you...",
  "conversation_id": 123,
  "message_id": 456,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔐 Security Architecture

### Authentication & Authorization

#### JWT Token Structure
```json
{
  "sub": "123",           // User ID
  "email": "user@example.com",
  "role": "user",
  "type": "access",       // access or refresh
  "exp": 1704067200,      // Expiration timestamp
  "iat": 1704063600       // Issued at timestamp
}
```

#### Security Headers
```python
# CORS Configuration
CORS_ALLOW_ORIGINS = ["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE"]
CORS_ALLOW_HEADERS = ["*"]

# Security Headers
SECURE_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}
```

### Rate Limiting Strategy

#### Per-User Limits
```python
# Rate limiting configuration
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000
RATE_LIMIT_PER_DAY = 10000
```

#### Implementation
```python
@limiter.limit("60/minute")
@router.post("/chat/send")
async def send_message(request: Request, ...):
    # Rate limited endpoint
    pass
```

### Data Protection

#### GDPR Compliance
- **Data Minimization**: Only collect necessary data
- **Consent Management**: Track user consent
- **Right to be Forgotten**: Data deletion capabilities
- **Data Portability**: Export user data
- **Audit Logging**: Track data access

#### Encryption
- **At Rest**: Database encryption
- **In Transit**: TLS 1.3
- **Passwords**: bcrypt hashing
- **Tokens**: JWT with secure algorithms

## 🤖 AI Integration

### OpenAI GPT-4 Integration

#### Request Structure
```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message},
    {"role": "assistant", "content": previous_response},
    {"role": "user", "content": current_message}
]

response = await openai.ChatCompletion.acreate(
    model="gpt-4-turbo-preview",
    messages=messages,
    max_tokens=1000,
    temperature=0.7,
    stream=False
)
```

#### Context Management
```python
def build_conversation_context(message, history, user_context):
    context = []
    
    # Add system prompt
    context.append({
        "role": "system",
        "content": get_system_prompt(user_context.get("language", "en"))
    })
    
    # Add conversation history (last 10 messages)
    for msg in history[-10:]:
        role = "user" if msg["type"] == "user" else "assistant"
        context.append({
            "role": role,
            "content": msg["content"]
        })
    
    # Add current message
    context.append({
        "role": "user",
        "content": message
    })
    
    return context
```

### Semantic Search

#### Embedding Generation
```python
async def generate_embeddings(text: str) -> List[float]:
    response = await openai.Embedding.acreate(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding
```

#### Similarity Search
```python
async def search_semantic(query: str, limit: int = 5):
    # Generate query embedding
    query_embedding = await generate_embeddings(query)
    
    # Search using vector similarity
    results = await db.execute("""
        SELECT id, question, answer, 
               1 - (question_embedding <=> $1) as similarity
        FROM faqs 
        WHERE status = 'published'
        ORDER BY question_embedding <=> $1
        LIMIT $2
    """, query_embedding, limit)
    
    return results
```

### Content Moderation

#### Moderation API
```python
async def moderate_content(text: str):
    response = await openai.Moderation.acreate(input=text)
    return {
        "flagged": response.results[0].flagged,
        "categories": response.results[0].categories,
        "category_scores": response.results[0].category_scores
    }
```

## ⚡ Performance Considerations

### Caching Strategy

#### Redis Cache Layers
```python
# Session Cache
session_cache = {
    "user:123:session": "session_data",
    "user:123:preferences": "user_preferences"
}

# Response Cache
response_cache = {
    "faq:search:query_hash": "search_results",
    "analytics:dashboard": "dashboard_data"
}

# Embedding Cache
embedding_cache = {
    "embedding:text_hash": "vector_data"
}
```

#### Cache Invalidation
```python
async def invalidate_user_cache(user_id: int):
    await redis.delete(f"user:{user_id}:session")
    await redis.delete(f"user:{user_id}:preferences")

async def invalidate_faq_cache():
    await redis.delete("faq:search:*")
```

### Database Optimization

#### Connection Pooling
```python
# Database configuration
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600
}
```

#### Query Optimization
```python
# Efficient conversation query
async def get_conversations_with_messages(user_id: int, limit: int = 10):
    query = """
        SELECT c.*, 
               COUNT(m.id) as message_count,
               MAX(m.created_at) as last_message_at
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.user_id = :user_id
        GROUP BY c.id
        ORDER BY c.last_message_at DESC
        LIMIT :limit
    """
    return await db.execute(query, {"user_id": user_id, "limit": limit})
```

### AI Response Optimization

#### Token Management
```python
class TokenManager:
    def __init__(self):
        self.max_tokens = 1000
        self.conversation_history_limit = 10
    
    def estimate_tokens(self, text: str) -> int:
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def truncate_history(self, messages: List[dict]) -> List[dict]:
        total_tokens = sum(self.estimate_tokens(msg["content"]) for msg in messages)
        
        while total_tokens > self.max_tokens and len(messages) > 1:
            # Remove oldest message (keep system prompt)
            removed = messages.pop(1)
            total_tokens -= self.estimate_tokens(removed["content"])
        
        return messages
```

## 📈 Scalability Strategy

### Horizontal Scaling

#### Load Balancer Configuration
```nginx
upstream chatbot_backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    server_name api.chatbot.com;
    
    location / {
        proxy_pass http://chatbot_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Database Sharding Strategy
```python
# User-based sharding
def get_shard_key(user_id: int) -> str:
    return f"shard_{user_id % 10}"

# Conversation sharding
def get_conversation_shard(conversation_id: int) -> str:
    return f"shard_{conversation_id % 10}"
```

### Vertical Scaling

#### Resource Allocation
```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

#### Auto-scaling Configuration
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chatbot-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chatbot-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 🚀 Deployment Architecture

### Container Orchestration

#### Docker Configuration
```dockerfile
FROM python:3.11-slim

# Security: Non-root user
RUN adduser --disabled-password --gecos '' appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Kubernetes Deployment
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
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
name: Deploy Chatbot Backend

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest tests/
    - name: Run linting
      run: flake8 app/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Build and push Docker image
      run: |
        docker build -t chatbot-backend .
        docker tag chatbot-backend:latest ${{ secrets.REGISTRY }}/chatbot-backend:${{ github.sha }}
        docker push ${{ secrets.REGISTRY }}/chatbot-backend:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/chatbot-backend chatbot-backend=${{ secrets.REGISTRY }}/chatbot-backend:${{ github.sha }}
```

## 📊 Monitoring & Observability

### Logging Strategy

#### Structured Logging
```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
logger.info(
    "User registered",
    user_id=user.id,
    email=user.email,
    ip_address=request.client.host
)
```

### Metrics Collection

#### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# AI metrics
AI_REQUEST_COUNT = Counter('ai_requests_total', 'Total AI requests')
AI_RESPONSE_TIME = Histogram('ai_response_time_seconds', 'AI response time')
AI_TOKEN_USAGE = Counter('ai_tokens_used_total', 'Total tokens used')

# Database metrics
DB_CONNECTION_GAUGE = Gauge('db_connections_active', 'Active database connections')
```

### Health Checks

#### Comprehensive Health Check
```python
@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database health
    try:
        await db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis health
    try:
        await redis.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # OpenAI health
    try:
        await openai.Model.aretrieve("gpt-4-turbo-preview")
        health_status["checks"]["openai"] = "healthy"
    except Exception as e:
        health_status["checks"]["openai"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status
```

### Alerting

#### Alert Rules
```yaml
# Prometheus alert rules
groups:
- name: chatbot_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"
  
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, http_request_duration_seconds) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"
  
  - alert: DatabaseConnectionIssues
    expr: db_connections_active < 1
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database connection issues"
      description: "No active database connections"
```

## 🔄 Future Enhancements

### Planned Improvements

1. **Microservices Architecture**
   - Split into separate services (auth, chat, analytics)
   - Service mesh implementation
   - Event-driven architecture

2. **Advanced AI Features**
   - Multi-modal support (images, voice)
   - Custom fine-tuned models
   - Advanced conversation memory

3. **Enhanced Analytics**
   - Real-time dashboards
   - Predictive analytics
   - A/B testing framework

4. **Security Enhancements**
   - Zero-trust architecture
   - Advanced threat detection
   - Compliance automation

5. **Performance Optimizations**
   - GraphQL implementation
   - Advanced caching strategies
   - CDN integration

This architecture provides a solid foundation for a scalable, secure, and maintainable AI chatbot system that can handle production workloads while maintaining high performance and reliability. 