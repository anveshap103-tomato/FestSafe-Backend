# FestSafe AI API Documentation

## Base URL

- Development: `http://localhost:8000/api/v1`
- Production: `https://api.festsafe.ai/api/v1`

## Authentication

All endpoints (except `/auth/login` and `/auth/register`) require authentication via JWT token.

Include the token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST /auth/login
Login and get access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /auth/register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "HospitalOps"
}
```

#### GET /auth/me
Get current user information.

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "HospitalOps",
  "is_active": true
}
```

### Hospitals

#### GET /hospitals
Get all hospitals.

**Query Parameters:**
- `skip` (int): Number of records to skip
- `limit` (int): Maximum number of records to return

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Memorial Hospital",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "bed_count": 200,
    "icu_count": 20,
    "oxygen_capacity": 500,
    "doctors_count": 50,
    "nurses_count": 100,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /hospitals/{hospital_id}
Get a specific hospital.

#### POST /hospitals
Create a new hospital.

**Request:**
```json
{
  "name": "Memorial Hospital",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "bed_count": 200,
  "icu_count": 20,
  "oxygen_capacity": 500,
  "doctors_count": 50,
  "nurses_count": 100
}
```

### Events

#### GET /events
Get all events.

#### GET /events/{event_id}
Get a specific event.

#### POST /events
Create a new event.

**Request:**
```json
{
  "name": "Summer Music Festival",
  "event_type": "Festival",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "start_ts": "2024-07-01T10:00:00Z",
  "end_ts": "2024-07-03T22:00:00Z",
  "expected_attendance": 50000
}
```

### Forecasts

#### GET /forecasts/hospital/{hospital_id}
Get forecasts for a hospital.

**Query Parameters:**
- `window` (string): Forecast window (e.g., "24h", "6h", "1h")

**Response:**
```json
[
  {
    "id": "uuid",
    "hospital_id": "uuid",
    "event_id": "uuid",
    "forecast_horizon": 24,
    "predicted_arrivals": 15.5,
    "confidence": 0.85,
    "risk_category": "medium",
    "forecast_timestamp": "2024-01-01T12:00:00Z",
    "model_version": "1.0.0"
  }
]
```

#### POST /forecasts/hospital/{hospital_id}/predict
Generate a forecast for a hospital.

**Query Parameters:**
- `event_id` (uuid, optional): Associated event
- `window` (string): Forecast window

### Recommendations

#### GET /recommendations
Get recommendations.

**Query Parameters:**
- `hospital_id` (uuid, optional)
- `event_id` (uuid, optional)
- `status` (string, optional): proposed, approved, rejected, modified

#### POST /recommendations
Create a recommendation.

**Request:**
```json
{
  "hospital_id": "uuid",
  "event_id": "uuid",
  "recommended_staffing": {
    "doctors": 10,
    "nurses": 25
  },
  "recommended_supplies": {
    "beds": 20,
    "oxygen_liters": 500
  },
  "confidence": 0.85
}
```

#### PATCH /recommendations/{recommendation_id}
Update recommendation status.

**Request:**
```json
{
  "status": "approved"
}
```

### Agents

#### POST /agents/ask
Send observation to multi-agent system.

**Request:**
```json
{
  "observation": {
    "hospital_id": "uuid",
    "event_id": "uuid",
    "current_metrics": {
      "current_patients": 50,
      "new_arrivals": 5,
      "primary_complaint_codes": ["R50.9", "R06.02"]
    },
    "environmental_context": {
      "aqi": 75,
      "temperature": 25,
      "humidity": 60
    }
  }
}
```

**Response:**
```json
{
  "action_plan": {
    "recommended_staffing": {
      "doctors": 10,
      "nurses": 25
    },
    "recommended_supplies": {
      "beds": 20,
      "oxygen_liters": 500
    },
    "confidence": 0.85,
    "messages_for_public": [
      "High patient volume expected..."
    ],
    "suggested_triage_templates": [...],
    "evidence": [...],
    "agent_actions": [...]
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

**Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user

## WebSocket

### /ws/updates
Real-time updates for dashboard.

**Message Format:**
```json
{
  "type": "forecast_update",
  "hospital_id": "uuid",
  "data": {...}
}
```

## Interactive API Documentation

Visit `/docs` for Swagger UI or `/redoc` for ReDoc documentation.


