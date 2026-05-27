# CareClaim – System Architecture

**Version**: 1.0  
**Last Updated**: May 21, 2026

---

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          React Frontend (Vite + TypeScript)             │   │
│  │  - Login Page (Authentication)                          │   │
│  │  - Provider: Claim Submission & Status                  │   │
│  │  - Adjudicator: Review Queue & Decisions               │   │
│  │  - Admin: Dashboard & Analytics                        │   │
│  │  - Medical Director: Clinical Review                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────────┘
                 │  HTTP/REST (JSON)
                 │  Port 5173 (Dev) → Port 3000 (Prod)
┌────────────────┴────────────────────────────────────────────────┐
│                         API LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          FastAPI Backend (Python 3.11)                 │   │
│  │  Port 8000                                             │   │
│  │                                                        │   │
│  │  ┌────────────────────────────────────────────────┐   │   │
│  │  │  API Routes                                    │   │   │
│  │  │  - /api/v1/auth/*       Authentication        │   │   │
│  │  │  - /api/v1/pa/*         Claim Processing      │   │   │
│  │  │  - /api/v1/data/*       Reference Data        │   │   │
│  │  └────────────────────────────────────────────────┘   │   │
│  │                                                        │   │
│  │  ┌────────────────────────────────────────────────┐   │   │
│  │  │  Business Logic                                │   │   │
│  │  │  - Claim Validation Service                   │   │   │
│  │  │  - OCR Processing Service                     │   │   │
│  │  │  - Report Generation Service                 │   │   │
│  │  │  - Fraud Scoring Service                     │   │   │
│  │  │  - Notification Service                      │   │   │
│  │  │  - AI Analysis Service                       │   │   │
│  │  └────────────────────────────────────────────────┘   │   │
│  │                                                        │   │
│  │  ┌────────────────────────────────────────────────┐   │   │
│  │  │  AI Agents                                     │   │   │
│  │  │  - Agent A: Document Processing & OCR        │   │   │
│  │  │  - Agent B: Policy Compliance Check           │   │   │
│  │  │  - Agent C: Risk & Fraud Analysis            │   │   │
│  │  │  - Orchestrator: Coordination Engine          │   │   │
│  │  │  - Policy Selector: Dynamic Routing           │   │   │
│  │  └────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────┬──────────────┬─────────────────┬───────────────────┘
             │              │                 │
    ┌────────┴──┐  ┌────────┴────┐  ┌────────┴─────┐
    │ Databases │  │   Caching   │  │  (Optional)  │
    │           │  │             │  │              │
┌───┴───┐  ┌────┴──┐  ┌──────────┴─┐
│SQLite │  │Post-  │  │   Redis    │
│(Dev)  │  │greSQL │  │  Cache     │
│       │  │(Prod) │  │ (Optional) │
└───────┘  │       │  └────────────┘
           │MongoDB│
           │(Opt)  │
           └───────┘
```

---

## 🔄 Claim Processing Workflow

```
1. PROVIDER SUBMISSION
   ├─ Login with credentials
   ├─ Fill claim form (patient, provider, dates, codes)
   ├─ Upload medical documents
   └─ Submit for processing

2. DOCUMENT PROCESSING (Agent A)
   ├─ Receive uploaded documents
   ├─ Extract text using OCR
   ├─ Clean and normalize text
   ├─ Classify document type
   └─ Return structured text + confidence

3. VALIDATION (Agent B)
   ├─ Check claim completeness
   ├─ Verify provider credentials
   ├─ Verify patient eligibility
   ├─ Check policy coverage
   ├─ Detect duplicate claims
   └─ Return validation results

4. RISK ANALYSIS (Agent C)
   ├─ Analyze medical necessity
   ├─ Check for fraud patterns
   ├─ Run anomaly detection
   ├─ Calculate fraud risk score
   ├─ Assess clinical appropriateness
   └─ Return risk metrics

5. DECISION ENGINE
   ├─ Aggregate all scores
   ├─ Score >= 85: AUTO-APPROVE ✓
   ├─ Score 60-85: HUMAN REVIEW ⚠
   ├─ Score < 60:  AUTO-DENY ✗
   └─ Route accordingly

6. ADJUDICATION (if needed)
   ├─ Adjudicator reviews claim
   ├─ Reviews documents & scores
   ├─ Makes final decision
   ├─ Adds notes/justification
   └─ Decision recorded

7. NOTIFICATION
   ├─ Send result to provider
   ├─ Log decision in audit trail
   ├─ Update claim status
   └─ Generate report
```

---

## 🏗️ Backend Architecture

### Directory Structure
```
backend/
├── api/                    # FastAPI application
│   ├── main.py            # Application entry point
│   ├── middleware/        # CORS, auth middleware
│   ├── routes/            # Endpoint definitions
│   │   ├── auth_routes.py    # Authentication endpoints
│   │   ├── pa_routes.py      # Claim processing endpoints
│   │   └── data_routes.py    # Reference data endpoints
│   └── schemas/           # Pydantic request/response models
│
├── agents/                # AI Agent implementations
│   ├── agent_a.py        # Document Processing Agent
│   ├── agent_b.py        # Policy Compliance Agent
│   ├── agent_c.py        # Risk Analysis Agent
│   ├── orchestrator.py    # Agent Coordination
│   └── policy_selector.py # Dynamic Routing
│
├── services/             # Business logic services
│   ├── ocr_service.py        # OCR text extraction
│   ├── scoring_service.py     # Risk scoring
│   ├── report_service.py      # Report generation
│   ├── notification_service.py # Notifications
│   └── sonar_service.py       # External API integration
│
├── core/                 # Core utilities
│   ├── config.py        # Configuration (Pydantic BaseSettings)
│   ├── database.py       # Database connections
│   ├── security.py       # JWT, hashing, security
│   ├── exceptions.py     # Custom exceptions
│   └── redis_client.py   # Redis connection
│
├── models/              # Database models
│   ├── postgres_models.py # SQLAlchemy models
│   └── mongo_models.py    # MongoDB models
│
├── workflows/           # Business workflows
│   └── claim_processing.py # Claim validation & scoring
│
└── uploads/             # Document storage
    └── {uuid}/          # Organized by upload ID
```

### Technology Stack
- **Framework**: FastAPI 0.136.1
- **Server**: Uvicorn 0.47.0
- **Database ORM**: SQLAlchemy 2.0.49
- **Validation**: Pydantic 2.13.4
- **Authentication**: python-jose (JWT), bcrypt
- **OCR**: Tesseract, EasyOCR, pytesseract
- **ML/AI**: scikit-learn, pandas, numpy, torch
- **LLM**: langchain-openai, langchain-anthropic

---

## 🎨 Frontend Architecture

### Directory Structure
```
frontend/
├── src/
│   ├── pages/           # Page components (route endpoints)
│   │   ├── auth/           # Authentication pages
│   │   │   └── Login.tsx    # Login form
│   │   ├── provider/        # Provider pages
│   │   │   ├── PASubmissionForm.tsx
│   │   │   ├── PAStatus.tsx
│   │   │   └── AdjudicatorReview.tsx
│   │   ├── adjudicator/     # Adjudicator pages
│   │   │   ├── ReviewQueue.tsx
│   │   │   ├── ReviewDetail.tsx
│   │   │   └── DecisionPanel.tsx
│   │   └── admin/           # Admin pages
│   │       ├── Dashboard.tsx
│   │       ├── PAList.tsx
│   │       └── Analytics.tsx
│   │
│   ├── components/      # Reusable components
│   │   ├── layout/         # Layout components
│   │   │   ├── PageLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── index.ts
│   │   └── common/         # Common UI components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       ├── Table.tsx
│   │       ├── Card.tsx
│   │       ├── Select.tsx
│   │       ├── Badge.tsx
│   │       ├── TagInput.tsx
│   │       ├── Toast.tsx
│   │       ├── Spinner.tsx
│   │       ├── Skeleton.tsx
│   │       ├── EmptyState.tsx
│   │       └── index.ts
│   │
│   ├── services/       # API client services
│   │   ├── api.ts          # Axios configuration
│   │   ├── auth.ts         # Authentication service
│   │   └── pa.service.ts   # Claim processing service
│   │
│   ├── hooks/          # Custom React hooks
│   │   ├── useAuth.ts      # Authentication hook
│   │   ├── usePA.ts        # Claim operations hook
│   │   ├── useNotifications.ts # Notifications
│   │   ├── useAnalytics.tsx    # Analytics data
│   │   └── index.ts
│   │
│   ├── context/        # React contexts (global state)
│   │   ├── AuthContext.tsx      # Auth state
│   │   ├── NotificationContext.tsx # Notifications
│   │   ├── ProviderContext.tsx   # Provider data
│   │   └── index.ts
│   │
│   ├── types/          # TypeScript type definitions
│   │   ├── user.types.ts
│   │   ├── pa.types.ts
│   │   └── index.ts
│   │
│   ├── utils/          # Utility functions
│   │   ├── formatters.ts   # Formatting utilities
│   │   ├── validators.ts   # Validation utilities
│   │   └── index.ts
│   │
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
│
└── public/
    └── vite.svg        # Logo
```

### Technology Stack
- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.4.21
- **Language**: TypeScript 5.4.5
- **Routing**: React Router 6.11.2
- **State Management**: TanStack Query (React Query)
- **Form Management**: React Hook Form 7.48.0
- **Form Validation**: Zod 3.22.4
- **HTTP Client**: Axios 1.6.2
- **UI Components**: Lucide React (icons)
- **Styling**: Tailwind CSS 3.4.1
- **Dev Server**: Vite (auto-reload on save)

---

## 🔐 Authentication & Security

### JWT Authentication Flow
```
1. User submits credentials
   ↓
2. Backend validates (bcrypt hash comparison)
   ↓
3. Server generates JWT token with claims
   ↓
4. Token returned to frontend
   ↓
5. Frontend stores in localStorage
   ↓
6. Frontend adds token to request headers
   ↓
7. Backend validates token signature
   ↓
8. Request proceeds or rejected
```

### Security Features
- **Password Hashing**: bcrypt (salted, work factor 12)
- **JWT Tokens**: HS256 algorithm, 8-hour expiry
- **CORS**: Configured for frontend domain
- **HTTPS**: TLS/SSL in production
- **Role-Based Access Control (RBAC)**:
  - Provider: Submit and view own claims
  - Adjudicator: Review assigned claims
  - Admin: Full system access
  - Medical Director: Clinical review access

---

## 💾 Database Schema

### Core Tables (SQLite/PostgreSQL)
```
users
├── id (Primary Key)
├── email (Unique)
├── username
├── hashed_password (bcrypt)
├── role (Provider, Adjudicator, Admin, Director)
├── is_active
├── created_at
└── updated_at

claims (Prior Authorizations)
├── id (Primary Key)
├── status (SUBMITTED, PROCESSING, APPROVED, DENIED, REVIEW)
├── patient_member_id
├── provider_npi
├── payer_id
├── plan_id
├── claim_amount
├── service_date
├── uploaded_documents (JSON)
├── ai_score (0-100)
├── decision_reason
├── created_at
└── updated_at

claim_decisions
├── id (Primary Key)
├── claim_id (Foreign Key)
├── decision (APPROVED, DENIED, NEEDS_REVIEW)
├── decided_by (adjudicator_id)
├── notes
├── decided_at
└── audit_trail (JSON)

documents
├── id (Primary Key)
├── claim_id (Foreign Key)
├── file_name
├── file_size
├── file_path
├── ocr_text (extracted)
├── uploaded_at
└── processing_status
```

---

## 🔄 API Response Format

### Standard Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation successful",
  "timestamp": "2026-05-21T12:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email or password is incorrect",
    "details": {}
  },
  "timestamp": "2026-05-21T12:00:00Z"
}
```

---

## 🚀 Deployment Architecture

### Development
```
Local Machine
├── Backend: python -m uvicorn (port 8000)
├── Frontend: npm run dev (port 5173)
└── Database: SQLite (local file)
```

### Production
```
Cloud Infrastructure (AWS/GCP/Azure)
├── Backend Service
│   ├── FastAPI on Uvicorn
│   ├── Load Balancer (HTTPS)
│   ├── Auto-scaling (Kubernetes/ECS)
│   └── Health checks
├── Frontend (CDN)
│   ├── Static asset distribution
│   ├── Global edge caching
│   └── HTTPS everywhere
├── Databases
│   ├── PostgreSQL (primary)
│   ├── MongoDB (documents)
│   └── Redis (cache/sessions)
└── Supporting Services
    ├── Monitoring (CloudWatch/Datadog)
    ├── Logging (ELK/CloudWatch)
    ├── Error tracking (Sentry)
    └── Email service (SendGrid/SES)
```

---

## 📊 Performance Considerations

### Optimization Strategies
- **Frontend**: Code splitting, lazy loading, Vite optimizations
- **Backend**: Async request handling, connection pooling, caching
- **Database**: Indexing, query optimization, connection pooling
- **OCR**: Batch processing, async task queue (Redis)
- **Caching**: Redis for session/temporary data
- **CDN**: CloudFront for static assets

### Expected Performance
- Page Load: < 2 seconds
- API Response: < 500ms (avg)
- Login Flow: < 2 seconds
- Document Upload: < 5 seconds (per document)
- OCR Processing: < 30 seconds (per document)
- Claim Decision: < 10 seconds

---

## 🔄 Scalability

### Current Capacity (Single Server)
- Concurrent Users: 100-500
- Requests per Second: 50-100
- Documents per Day: 1,000-10,000
- Processing Latency: < 30 seconds

### At Scale (Production)
- Concurrent Users: 10,000+
- Requests per Second: 5,000+
- Documents per Day: 1,000,000+
- Processing Latency: < 5 seconds (with queuing)

### Scaling Strategies
- Horizontal scaling (load balancing)
- Async task processing (background workers)
- Database replication and sharding
- CDN for static assets
- API rate limiting
- Cache optimization

---

## 📋 Monitoring & Observability

### Metrics to Track
- Request latency (95th/99th percentile)
- Error rates (by endpoint)
- Database query performance
- OCR processing time
- Cache hit/miss ratios
- User authentication events
- System resource usage

### Logging
- All API requests/responses (debug level)
- Authentication events (security level)
- Database operations (performance level)
- OCR processing (info level)
- Errors and exceptions (error level)

### Alerting
- API error rate > 1%
- Response time > 1 second
- Database connection failures
- Service health check failures
- High CPU/memory usage
- Disk space low

---

## 🔮 Future Enhancements

1. **Microservices Architecture**
   - Separate OCR service
   - Dedicated ML service
   - Independent auth service

2. **Advanced ML**
   - Custom ML models for fraud detection
   - Natural language processing
   - Predictive analytics

3. **Integrations**
   - Insurance provider APIs
   - EHR/EMR systems
   - Payment processors

4. **Features**
   - Mobile app (iOS/Android)
   - API webhooks
   - Batch processing
   - Advanced reporting
   - Multi-language support

---

**Last Updated**: May 21, 2026  
**Architecture Version**: 1.0
