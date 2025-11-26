# FestSafe AI Architecture

## System Overview

FestSafe AI is a microservices-based SaaS platform for predictive hospital readiness management. The system is designed to be scalable, secure, and maintainable.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│                    Port 3000 / 80 (nginx)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Backend    │    │  ML Service  │    │   Workers    │
│   (FastAPI)  │    │  (PyTorch)   │    │   (Celery)   │
│   Port 8000  │    │   Port 8001  │    │              │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │   RabbitMQ   │
│  (Timescale) │  │   (Cache)    │  │  (Message)   │
└──────────────┘  └──────────────┘  └──────────────┘
        │
        ▼
┌──────────────┐
│  External    │
│  APIs        │
│  (AQI,       │
│   Weather)   │
└──────────────┘
```

## Data Flow

### 1. Data Ingestion
- External APIs (AQI, Weather) → Workers → PostgreSQL
- Event registration → Backend API → PostgreSQL
- Real-time observations → Backend API → PostgreSQL

### 2. Feature Engineering
- Historical observations → Feature Store (PostgreSQL)
- Event data → Feature Store
- Environmental data → Feature Store

### 3. Model Inference
- Feature Store → ML Service → Predictions → Backend API
- Predictions stored in PostgreSQL

### 4. Multi-Agent Orchestration
- Observations → Agent Orchestrator → Multiple Agents → Action Plan
- Action Plan → Recommendations → PostgreSQL

### 5. Frontend Display
- Backend API → Frontend → Real-time Dashboard
- WebSocket updates for live data

## Components

### Frontend
- **Technology**: React 18, TypeScript, Tailwind CSS
- **State Management**: React Query
- **Visualization**: Recharts, Mapbox GL
- **Build**: Vite

### Backend API
- **Technology**: FastAPI, Python 3.10+
- **Database**: PostgreSQL 14 (TimescaleDB extension)
- **Caching**: Redis
- **Message Queue**: RabbitMQ
- **Authentication**: JWT (OAuth2)

### ML Service
- **Technology**: PyTorch, scikit-learn
- **Model Serving**: Custom FastAPI service
- **Experiment Tracking**: MLflow
- **Inference**: Real-time and batch

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Kubernetes (EKS)
- **Infrastructure as Code**: Terraform
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana

## Security

- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-Based Access Control (RBAC)
- **Encryption**: TLS in transit, encryption at rest
- **PII Handling**: Anonymization on ingestion
- **Audit Logging**: All data access logged

## Scalability

- **Horizontal Scaling**: Kubernetes auto-scaling
- **Database**: Read replicas, connection pooling
- **Caching**: Redis for frequently accessed data
- **Message Queue**: RabbitMQ for async processing
- **CDN**: For static frontend assets

## Monitoring & Observability

- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: Centralized logging (Loki)
- **Tracing**: Distributed tracing (optional)
- **Alerting**: Prometheus Alertmanager

## Deployment

- **Development**: Docker Compose
- **Staging**: Kubernetes (EKS)
- **Production**: Kubernetes (EKS) with auto-scaling

## Data Retention

- **Raw Observations**: 90 days
- **Aggregated Data**: 1 year
- **Forecasts**: 30 days
- **Recommendations**: 90 days


