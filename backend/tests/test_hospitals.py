"""
Tests for hospital endpoints.
"""

import pytest
from fastapi import status


def test_get_hospitals(client, auth_headers, test_hospital):
    """Test getting all hospitals."""
    response = client.get("/api/v1/hospitals", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "Test Hospital"


def test_get_hospital(client, auth_headers, test_hospital):
    """Test getting a specific hospital."""
    response = client.get(
        f"/api/v1/hospitals/{test_hospital.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Test Hospital"


def test_create_hospital(client, auth_headers):
    """Test creating a hospital."""
    response = client.post(
        "/api/v1/hospitals",
        headers=auth_headers,
        json={
            "name": "New Hospital",
            "latitude": 37.7849,
            "longitude": -122.4094,
            "bed_count": 200,
            "icu_count": 20,
            "oxygen_capacity": 1000,
            "doctors_count": 40,
            "nurses_count": 100
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "New Hospital"


def test_get_hospital_not_found(client, auth_headers):
    """Test getting non-existent hospital."""
    import uuid
    response = client.get(
        f"/api/v1/hospitals/{uuid.uuid4()}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


