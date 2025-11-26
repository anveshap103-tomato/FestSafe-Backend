# FestSafe AI — Predictive Hospital Readiness Agent

A production-ready SaaS system that predicts hospital surge capacity, recommends resource allocation, provides public health advisories, and enables multi-agent healthcare intelligence for event-driven healthcare management.

## 🎯 Overview

FestSafe AI ingests real-time and historical data to:
- Predict hospital surge capacity for events (festivals, concerts, marathons)
- Recommend optimal resource allocation (staffing, supplies, beds)
- Provide public health advisories
- Enable multi-agent decision-making for healthcare operations

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend    │────▶│  ML Service │
│   (React)   │◀────│   (FastAPI)  │◀────│  (PyTorch)  │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  PostgreSQL  │
                    │ (TimescaleDB)│
                    └──────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
            ┌───────▼────┐  ┌──────▼──────┐
            │   Redis    │  │   Kafka/    │
            │  (Cache)   │  │  RabbitMQ   │
            └────────────┘  └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (or use Docker)
- Redis (or use Docker)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd "FestSafe AI"
   ```

2. **Start infrastructure services**
   ```bash
   docker-compose -f infra/docker-compose.dev.yml up -d
   ```

3. **Generate synthetic data**
   ```bash
   cd ml/training
   python data_simulator.py --hospitals 50 --events 10 --days 90
   ```

4. **Train initial model**
   ```bash
   python train.py --config configs/baseline.yaml
   ```

5. **Start backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

6. **Start frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

7. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Using Docker Compose (Recommended)

```bash
docker-compose -f infra/docker-compose.dev.yml up --build
```

## 📁 Project Structure

```
FestSafe AI/
├── frontend/          # React + TypeScript frontend
├── backend/           # FastAPI backend
├── ml/                # ML training and inference
│   ├── training/      # Model training scripts
│   └── inference/     # Model serving
├── infra/             # Infrastructure as code
│   ├── terraform/     # AWS infrastructure
│   └── k8s/           # Kubernetes manifests
├── ci/                # CI/CD workflows
├── docs/              # Documentation
└── tests/             # Integration and E2E tests
```

## 🔑 Key Features

- **Real-time Forecasting**: Predict patient surge with <500ms latency
- **Multi-Agent System**: Orchestrated agents for forecasting, triage, and communication
- **Event Management**: Register and track festivals, concerts, and other events
- **Resource Recommendations**: AI-powered staffing and supply suggestions
- **Public Health Advisories**: Automated communication for affected areas
- **HIPAA-Conscious Design**: Privacy-preserving defaults and encryption

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test

# Integration tests
pytest tests/integration/ -v
```

## 📊 Monitoring

- Prometheus metrics: http://localhost:9090
- Grafana dashboards: http://localhost:3001
- MLflow tracking: http://localhost:5000

## 🔒 Security

- JWT-based authentication
- RBAC (Role-Based Access Control)
- TLS encryption in transit
- Database encryption at rest
- PII anonymization on ingestion
- Audit logging

## 📚 Documentation

- [Architecture](./docs/architecture.md)
- [API Documentation](./docs/api.md)
- [Runbook](./docs/runbook.md)
- [Contributing](./CONTRIBUTING.md)

## 🛠️ Tech Stack

- **Frontend**: React, TypeScript, Tailwind CSS, React Query, Recharts, Mapbox GL
- **Backend**: FastAPI, PostgreSQL (TimescaleDB), Redis, RabbitMQ
- **ML**: PyTorch, scikit-learn, MLflow
- **Infrastructure**: Docker, Kubernetes, Terraform, AWS
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana, Loki, Sentry

## 📝 License

See [LICENSE](./LICENSE) file.

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## ⚠️ Medical Disclaimer

This system provides **suggestions and references only**. All medical decisions require clinician review and approval. The system does not provide prescriptive medical advice.


