# FestSafe AI Demo Guide

## Quick Start Demo

This guide walks you through running the complete FestSafe AI system locally.

## Prerequisites

- Docker & Docker Compose installed
- Python 3.10+ (for running scripts)
- Node.js 18+ (for frontend development, optional)

## Step 1: Start Infrastructure Services

```bash
cd infra
docker-compose -f docker-compose.dev.yml up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- RabbitMQ (port 5672, management UI: 15672)
- MLflow (port 5000)
- Prometheus (port 9090)
- Grafana (port 3001, admin/admin)

Wait for all services to be healthy (check with `docker-compose ps`).

## Step 2: Generate Synthetic Data

```bash
cd ml/training
pip install -r requirements.txt
python data_simulator.py --hospitals 50 --events 10 --days 90 --output-dir ../../data/synthetic
```

This creates:
- `data/synthetic/hospitals.json` (or .csv)
- `data/synthetic/events.json` (or .csv)
- `data/synthetic/observations.csv`

## Step 3: Train Initial Model

```bash
cd ml/training
python train.py --config configs/baseline.yaml --data-dir ../../data/synthetic --model-type tabular
```

This will:
- Load the synthetic data
- Train a gradient-boosted tree model
- Log experiments to MLflow (http://localhost:5000)

## Step 4: Set Up Backend

```bash
cd backend
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://festsafe:festsafe@localhost:5432/festsafe
SECRET_KEY=dev-secret-key-change-in-production
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
ML_SERVICE_URL=http://localhost:8001
EOF

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at http://localhost:8000
API docs at http://localhost:8000/docs

## Step 5: Seed Initial Data (Optional)

Create a Python script to load synthetic data into the database:

```python
# scripts/seed_data.py
import json
import sys
sys.path.append('../backend')
from app.db.database import SessionLocal
from app.db import crud, models
from app.core.security import get_password_hash

db = SessionLocal()

# Create admin user
admin = crud.create_user(db, {
    "email": "admin@festsafe.ai",
    "hashed_password": get_password_hash("admin123"),
    "full_name": "Admin User",
    "role": "Admin"
})

# Load hospitals
with open('../data/synthetic/hospitals.json') as f:
    hospitals = json.load(f)
    for h in hospitals:
        crud.create_hospital(db, {
            "name": h["name"],
            "latitude": h["location"]["lat"],
            "longitude": h["location"]["lon"],
            "bed_count": h["bed_count"],
            "icu_count": h["icu_count"],
            "oxygen_capacity": h["oxygen_capacity"],
            "doctors_count": h["staff_count"]["doctors"],
            "nurses_count": h["staff_count"]["nurses"]
        })

db.close()
```

Run: `python scripts/seed_data.py`

## Step 6: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:3000

## Step 7: Login and Explore

1. Open http://localhost:3000
2. Login with:
   - Email: `admin@festsafe.ai`
   - Password: `admin123`
3. Explore:
   - **Dashboard**: View hospitals on map
   - **Hospital Detail**: Click on a hospital to see forecasts
   - **Agent Console**: Run multi-agent system
   - **Settings**: Configure integrations

## Step 8: Generate Forecasts

Use the API to generate forecasts:

```bash
# Get hospitals
curl http://localhost:8000/api/v1/hospitals \
  -H "Authorization: Bearer YOUR_TOKEN"

# Generate forecast
curl -X POST "http://localhost:8000/api/v1/forecasts/hospital/HOSPITAL_ID/predict?window=24h" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Step 9: Test Multi-Agent System

```bash
curl -X POST http://localhost:8000/api/v1/agents/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "observation": {
      "hospital_id": "HOSPITAL_ID",
      "current_metrics": {
        "current_patients": 50,
        "new_arrivals": 5
      },
      "environmental_context": {
        "aqi": 75,
        "temperature": 25,
        "humidity": 60
      }
    }
  }'
```

## Monitoring

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **MLflow**: http://localhost:5000
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `docker-compose ps`
- Check connection string in `.env`

### Frontend Not Loading
- Check backend is running
- Verify API proxy in `vite.config.ts`

### Model Inference Failing
- Ensure model file exists at `MODEL_PATH`
- Check ML service logs

## Cleanup

```bash
# Stop all services
cd infra
docker-compose -f docker-compose.dev.yml down -v

# Remove data
rm -rf data/synthetic/*
```

## Video Walkthrough Script

1. **Introduction** (30s)
   - "Welcome to FestSafe AI, a predictive hospital readiness system"

2. **Dashboard Overview** (1min)
   - Show map with hospitals
   - Explain real-time monitoring

3. **Hospital Detail** (1min)
   - Click on hospital
   - Show forecasts and recommendations

4. **Agent Console** (1min)
   - Run multi-agent system
   - Show reasoning traces

5. **API Demo** (30s)
   - Show API documentation
   - Make a sample request

6. **Monitoring** (30s)
   - Show Grafana dashboards
   - Explain metrics

Total: ~5 minutes


