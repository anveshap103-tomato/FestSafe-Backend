"""
Script to seed database with initial data.
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.db.database import SessionLocal
from app.db import crud, models
from app.core.security import get_password_hash

def seed_data():
    """Seed database with initial data."""
    db = SessionLocal()
    
    try:
        # Create admin user
        admin_email = "admin@festsafe.ai"
        existing_user = crud.get_user_by_email(db, admin_email)
        if not existing_user:
            admin = crud.create_user(db, {
                "email": admin_email,
                "hashed_password": get_password_hash("admin123"),
                "full_name": "Admin User",
                "role": "Admin"
            })
            print(f"Created admin user: {admin.email}")
        else:
            print(f"Admin user already exists: {admin_email}")
        
        # Load hospitals from synthetic data
        hospitals_file = Path(__file__).parent.parent / "data" / "synthetic" / "hospitals.json"
        if hospitals_file.exists():
            with open(hospitals_file) as f:
                hospitals_data = json.load(f)
                for h in hospitals_data:
                    # Check if hospital already exists
                    existing = db.query(models.Hospital).filter(
                        models.Hospital.name == h["name"]
                    ).first()
                    if not existing:
                        hospital = crud.create_hospital(db, {
                            "name": h["name"],
                            "latitude": h["location"]["lat"],
                            "longitude": h["location"]["lon"],
                            "bed_count": h["bed_count"],
                            "icu_count": h["icu_count"],
                            "oxygen_capacity": h["oxygen_capacity"],
                            "doctors_count": h["staff_count"]["doctors"],
                            "nurses_count": h["staff_count"]["nurses"]
                        })
                        print(f"Created hospital: {hospital.name}")
                    else:
                        print(f"Hospital already exists: {h['name']}")
        else:
            print(f"Hospitals file not found: {hospitals_file}")
        
        # Load events
        events_file = Path(__file__).parent.parent / "data" / "synthetic" / "events.json"
        if events_file.exists():
            with open(events_file) as f:
                events_data = json.load(f)
                for e in events_data:
                    existing = db.query(models.Event).filter(
                        models.Event.name == e["name"]
                    ).first()
                    if not existing:
                        event = crud.create_event(db, {
                            "name": e["name"],
                            "event_type": e["event_type"],
                            "latitude": e["location"]["lat"],
                            "longitude": e["location"]["lon"],
                            "start_ts": e["start_ts"],
                            "end_ts": e["end_ts"],
                            "expected_attendance": e["expected_attendance"]
                        })
                        print(f"Created event: {event.name}")
                    else:
                        print(f"Event already exists: {e['name']}")
        else:
            print(f"Events file not found: {events_file}")
        
        print("Data seeding complete!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()


