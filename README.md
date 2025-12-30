# URL Shortener - Production Ready

A full-stack URL shortening service with Redis caching, analytics, and a modern React frontend.

## 🚀 Features

- ✅ **URL Shortening** - Create short URLs with custom codes
- ✅ **User Authentication** - JWT-based secure authentication
- ✅ **Redis Caching** - High-performance URL lookups
- ✅ **Analytics Dashboard** - Track clicks and performance
- ✅ **Expiring Links** - Set expiration dates for URLs
- ✅ **Rate Limiting** - Protect against abuse
- ✅ **Modern Frontend** - React + Vite + Tailwind CSS
- ✅ **Docker Support** - Easy deployment with Docker Compose
- ✅ **CI/CD Pipeline** - Automated testing and deployment

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/varsha2176/url-shortener.git
cd url-shortener
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the backend**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Create environment file**
```bash
echo "VITE_API_URL=http://localhost:8000" > .env
```

4. **Start development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Manual Docker Build
```bash
# Build backend image
docker build -t url-shortener-backend .

# Run backend container
docker run -d -p 8000:8000 --env-file .env url-shortener-backend
```

## 🧪 Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run tests with coverage
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_urls.py -v
```

## 📊 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user

#### URLs
- `POST /api/v1/urls/` - Create short URL
- `GET /api/v1/urls/` - List user's URLs
- `GET /api/v1/urls/{short_code}` - Get URL details
- `DELETE /api/v1/urls/{short_code}` - Delete URL
- `GET /{short_code}` - Redirect to original URL

#### Analytics
- `GET /api/v1/analytics/{short_code}` - Get URL analytics
- `GET /api/v1/analytics/top` - Get top URLs
- `GET /api/v1/analytics/dashboard` - Get dashboard stats

## 🌐 Deployment

### Deploy to Vercel (Frontend)

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy frontend**
```bash
cd frontend
vercel --prod
```

3. **Set environment variables in Vercel Dashboard**
```
VITE_API_URL=https://your-backend-url.com
```

### Deploy Backend (Railway/Render/Heroku)

1. **Create new app on your platform**

2. **Set environment variables**
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=your-secret-key
BASE_URL=https://your-domain.com
```

3. **Deploy using Git**
```bash
git push railway main  # or render/heroku
```

## 🔧 Configuration

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/urlshortener

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
BASE_URL=http://localhost:8000
ENVIRONMENT=development
```

## 📈 Performance

- **Redis Caching**: URL lookups cached for instant redirects
- **Database Indexing**: Optimized queries with proper indexes
- **Rate Limiting**: 100 requests per minute per IP
- **Connection Pooling**: Efficient database connections

## 🔒 Security

- JWT authentication with secure token handling
- Password hashing with bcrypt
- CORS configuration for frontend
- Rate limiting to prevent abuse
- SQL injection protection with SQLAlchemy ORM
- XSS protection with input validation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Aruna Varsha  - [@varsha2176](https://github.com/varsha2176)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React and Vite for the frontend
- Redis for caching capabilities
- PostgreSQL for reliable data storage
