# CareClaim – Getting Started Guide

**Welcome to CareClaim!** This guide will help you set up and run the system locally in 5 minutes.

---

## 📦 Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **Tesseract OCR** (for OCR functionality - optional for testing)

### Install Tesseract (Optional)
- **Windows**: Download from [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ClaimCare
```

### 2. Backend Setup
```bash
cd pa-workflow/backend

# Install dependencies
pip install -r requirements.txt

# Set environment
set PYTHONPATH=%cd%

# Run server
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup (New Terminal)
```bash
cd pa-workflow/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🔐 Default Credentials

Test the system with these demo accounts (password: `password`):

| Email | Role | Permissions |
|-------|------|-------------|
| `provider@example.com` | Provider | Submit prior auth requests |
| `adjudicator@example.com` | Adjudicator | Review and adjudicate claims |
| `admin@example.com` | Admin | System administration |
| `director@example.com` | Medical Director | Medical director review |

---

## 📋 Project Structure

```
CareClaim/
├── pa-workflow/
│   ├── backend/              # FastAPI backend server
│   │   ├── api/              # API routes & endpoints
│   │   ├── agents/           # AI agents for processing
│   │   ├── services/         # Business logic services
│   │   ├── core/             # Configuration & utilities
│   │   ├── models/           # Database models
│   │   ├── workflows/        # Claim processing workflows
│   │   ├── .env              # Environment configuration
│   │   └── requirements.txt  # Python dependencies
│   │
│   ├── frontend/             # React frontend application
│   │   ├── src/
│   │   │   ├── pages/        # Page components
│   │   │   ├── components/   # Reusable components
│   │   │   ├── services/     # API client services
│   │   │   └── App.tsx       # Main app component
│   │   ├── package.json      # Node dependencies
│   │   └── vite.config.ts    # Build configuration
│   │
│   ├── README.md             # Workflow documentation
│   └── WORKFLOW_GUIDE.md     # Complete workflow guide
│
├── README.md                 # Main project documentation
├── LICENSE                   # MIT License
└── .env.example             # Environment template
```

---

## 🛠️ Backend Configuration

### Environment Variables (.env)

The `.env` file in `pa-workflow/backend/` contains:

```env
# Mode: dev, staging, prod
ENVIRONMENT=dev

# Database (SQLite by default)
POSTGRES_DB=careclaim
POSTGRES_USER=careclaim_user
POSTGRES_PASSWORD=password

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# OCR
OCR_ENGINE=tesseract
OCR_CONFIDENCE_THRESHOLD=0.70

# Optional Services (commented out by default)
# MONGO_URI=mongodb://localhost:27017/careclaim
# REDIS_URL=redis://localhost:6379/0
```

### Database

- **Development**: SQLite (file-based, no setup needed)
- **Production**: PostgreSQL (configured via POSTGRES_* env vars)
- **Optional**: MongoDB for document storage

---

## 🎨 Frontend Configuration

### Environment Variables (.env in frontend/)

```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

### Development Tools

- **Vite**: Lightning-fast build tool
- **React Router**: Client-side routing
- **TanStack Query**: Server state management
- **React Hook Form**: Form validation
- **Tailwind CSS**: Utility-first CSS framework

---

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh token

### Claim Processing
- `POST /api/v1/pa/submit` - Submit prior authorization
- `GET /api/v1/pa/{pa_id}` - Get claim status
- `GET /api/v1/pa` - List claims
- `POST /api/v1/pa/{pa_id}/adjudicate` - Adjudicate claim

### Data Reference
- `GET /api/v1/data/payers` - Insurance payers
- `GET /api/v1/data/plans` - Insurance plans
- `GET /api/v1/data/procedures` - Medical procedures

**Full API Documentation**: http://localhost:8000/docs (Swagger UI)

---

## 🔍 Testing the System

### 1. Test Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "provider@example.com",
    "password": "password"
  }'
```

### 2. Test Upload & Processing
- Navigate to http://localhost:5173
- Login as provider@example.com
- Click "Submit Claim"
- Upload a medical document
- View AI-powered analysis

### 3. Test Admin Dashboard
- Login as admin@example.com
- View analytics and claim statistics

### 4. Test Adjudication
- Login as adjudicator@example.com
- Review pending claims
- Make adjudication decisions

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Module Import Errors
```bash
# Ensure PYTHONPATH is set to backend directory
set PYTHONPATH=c:\path\to\backend

# Or use this command instead:
python -m uvicorn api.main:app
```

### Database Errors
```bash
# Delete old SQLite database
rm pa-workflow/backend/careclaim.db

# Restart backend (creates new database)
```

### Frontend Not Loading
```bash
# Clear node_modules and reinstall
cd pa-workflow/frontend
rm -r node_modules package-lock.json
npm install
npm run dev
```

### API Connection Issues
- Ensure backend is running on http://127.0.0.1:8000
- Check Vite proxy configuration in vite.config.ts
- Verify CORS settings in api/main.py

---

## 📚 Next Steps

1. **Read the Documentation**
   - [WORKFLOW_GUIDE.md](pa-workflow/WORKFLOW_GUIDE.md) - Complete workflow documentation
   - [README.md](README.md) - Full project documentation

2. **Explore the Code**
   - Start with `pa-workflow/backend/api/routes/auth_routes.py`
   - Then check `pa-workflow/frontend/src/pages/auth/Login.tsx`

3. **Understand the Workflow**
   - Review `pa-workflow/backend/workflows/claim_processing.py`
   - Check the agent implementations in `pa-workflow/backend/agents/`

4. **Deploy to Production**
   - Configure PostgreSQL database
   - Set up MongoDB for document storage
   - Configure Redis for caching
   - Deploy with Docker or cloud platform

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Test thoroughly
4. Create a pull request

---

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review [WORKFLOW_GUIDE.md](pa-workflow/WORKFLOW_GUIDE.md)
- Contact the development team

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

**Last Updated**: May 21, 2026
