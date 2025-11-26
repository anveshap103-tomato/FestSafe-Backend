"""
Data Simulator for FestSafe AI
Generates synthetic hospital, event, and observation data for development and testing.
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import uuid
import numpy as np
import pandas as pd


class DataSimulator:
    """Generate synthetic data for hospitals, events, and observations."""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        self.hospitals: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self.observations: List[Dict[str, Any]] = []
        
    def generate_hospitals(self, count: int, city_bounds: Dict[str, float] = None) -> List[Dict]:
        """Generate synthetic hospital data."""
        if city_bounds is None:
            city_bounds = {"lat_min": 37.7, "lat_max": 37.8, "lon_min": -122.5, "lon_max": -122.4}
        
        hospital_types = ["General", "Emergency", "Trauma Center", "Community"]
        names = ["Memorial", "General", "Regional", "Community", "City", "County", "University"]
        
        hospitals = []
        for i in range(count):
            hospital = {
                "id": str(uuid.uuid4()),
                "name": f"{random.choice(names)} {random.choice(hospital_types)} Hospital",
                "location": {
                    "lat": random.uniform(city_bounds["lat_min"], city_bounds["lat_max"]),
                    "lon": random.uniform(city_bounds["lon_min"], city_bounds["lon_max"])
                },
                "bed_count": random.randint(50, 500),
                "icu_count": random.randint(5, 50),
                "oxygen_capacity": random.randint(100, 1000),  # liters
                "staff_count": {
                    "doctors": random.randint(10, 100),
                    "nurses": random.randint(20, 200)
                },
                "contact_info": {
                    "phone_hash": f"hash_{random.randint(1000000, 9999999)}",  # Anonymized
                    "email_hash": f"hash_{random.randint(1000000, 9999999)}"
                },
                "created_at": datetime.now().isoformat()
            }
            hospitals.append(hospital)
        
        self.hospitals = hospitals
        return hospitals
    
    def generate_events(self, count: int, start_date: datetime, days_ahead: int = 30) -> List[Dict]:
        """Generate synthetic event data."""
        event_types = ["Festival", "Concert", "Marathon", "Sports Event", "Conference", "Parade"]
        event_names = [
            "Summer Music Festival", "City Marathon", "Jazz Concert", "Food & Wine Festival",
            "Tech Conference", "Cultural Parade", "Sports Championship", "Art Fair"
        ]
        
        events = []
        for i in range(count):
            event_start = start_date + timedelta(days=random.randint(0, days_ahead))
            event_duration = random.choice([1, 2, 3, 5])  # days
            event_end = event_start + timedelta(days=event_duration)
            
            event = {
                "id": str(uuid.uuid4()),
                "name": random.choice(event_names),
                "event_type": random.choice(event_types),
                "location": {
                    "lat": random.uniform(37.7, 37.8),
                    "lon": random.uniform(-122.5, -122.4)
                },
                "start_ts": event_start.isoformat(),
                "end_ts": event_end.isoformat(),
                "expected_attendance": random.randint(1000, 100000),
                "created_at": datetime.now().isoformat()
            }
            events.append(event)
        
        self.events = events
        return events
    
    def generate_observations(
        self, 
        hospitals: List[Dict], 
        start_date: datetime, 
        days: int,
        interval_hours: int = 1
    ) -> List[Dict]:
        """Generate time-series observation data."""
        observations = []
        current_date = start_date
        end_date = start_date + timedelta(days=days)
        
        # ICD-10 complaint codes (simplified)
        complaint_codes = [
            "R50.9",  # Fever
            "R06.02",  # Shortness of breath
            "R51",     # Headache
            "R10.9",   # Abdominal pain
            "I10",     # Hypertension
            "E11.9",   # Type 2 diabetes
            "J44.9",   # COPD
            "I50.9",   # Heart failure
        ]
        
        while current_date < end_date:
            for hospital in hospitals:
                # Base arrival rate
                base_arrivals = np.random.poisson(2)
                
                # Event impact (if any active events nearby)
                event_multiplier = 1.0
                for event in self.events:
                    event_start = datetime.fromisoformat(event["start_ts"])
                    event_end = datetime.fromisoformat(event["end_ts"])
                    if event_start <= current_date <= event_end:
                        # Distance-based impact
                        distance = np.sqrt(
                            (hospital["location"]["lat"] - event["location"]["lat"])**2 +
                            (hospital["location"]["lon"] - event["location"]["lon"])**2
                        )
                        if distance < 0.1:  # Within ~10km
                            event_multiplier += event["expected_attendance"] / 100000
                
                # Environmental factors
                aqi = random.uniform(20, 150)  # Air Quality Index
                temperature = random.uniform(15, 35)  # Celsius
                humidity = random.uniform(30, 90)  # Percentage
                
                # Environmental impact on arrivals
                if aqi > 100:
                    base_arrivals *= 1.2
                if temperature > 30:
                    base_arrivals *= 1.1
                
                arrivals = max(0, int(base_arrivals * event_multiplier))
                
                # Current patients (simulated occupancy)
                bed_capacity = hospital["bed_count"]
                occupancy_rate = random.uniform(0.4, 0.9)
                current_patients = int(bed_capacity * occupancy_rate)
                
                # Age distribution
                avg_age = random.uniform(35, 75)
                
                # Primary complaints
                primary_complaints = random.sample(
                    complaint_codes, 
                    k=min(len(complaint_codes), arrivals)
                ) if arrivals > 0 else []
                
                observation = {
                    "id": str(uuid.uuid4()),
                    "timestamp": current_date.isoformat(),
                    "hospital_id": hospital["id"],
                    "current_patients": current_patients,
                    "new_arrivals": arrivals,
                    "avg_age": round(avg_age, 1),
                    "primary_complaint_codes": primary_complaints[:5],  # Top 5
                    "environmental_context": {
                        "aqi": round(aqi, 1),
                        "temperature": round(temperature, 1),
                        "humidity": round(humidity, 1)
                    },
                    "created_at": datetime.now().isoformat()
                }
                observations.append(observation)
            
            current_date += timedelta(hours=interval_hours)
        
        self.observations = observations
        return observations
    
    def save_to_json(self, output_dir: Path):
        """Save generated data to JSON files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "hospitals.json", "w") as f:
            json.dump(self.hospitals, f, indent=2)
        
        with open(output_dir / "events.json", "w") as f:
            json.dump(self.events, f, indent=2)
        
        # Save observations in chunks (can be large)
        chunk_size = 10000
        for i in range(0, len(self.observations), chunk_size):
            chunk = self.observations[i:i + chunk_size]
            filename = output_dir / f"observations_chunk_{i // chunk_size}.json"
            with open(filename, "w") as f:
                json.dump(chunk, f, indent=2)
        
        print(f"Saved {len(self.hospitals)} hospitals, {len(self.events)} events, "
              f"and {len(self.observations)} observations to {output_dir}")
    
    def save_to_csv(self, output_dir: Path):
        """Save generated data to CSV files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Flatten hospital data
        hospitals_df = pd.DataFrame([
            {
                **h,
                "lat": h["location"]["lat"],
                "lon": h["location"]["lon"],
                "doctors": h["staff_count"]["doctors"],
                "nurses": h["staff_count"]["nurses"]
            }
            for h in self.hospitals
        ])
        hospitals_df = hospitals_df.drop(columns=["location", "staff_count", "contact_info"])
        hospitals_df.to_csv(output_dir / "hospitals.csv", index=False)
        
        # Flatten event data
        events_df = pd.DataFrame([
            {
                **e,
                "lat": e["location"]["lat"],
                "lon": e["location"]["lon"]
            }
            for e in self.events
        ])
        events_df = events_df.drop(columns=["location"])
        events_df.to_csv(output_dir / "events.csv", index=False)
        
        # Flatten observations
        observations_data = []
        for obs in self.observations:
            env = obs["environmental_context"]
            observations_data.append({
                **obs,
                "aqi": env["aqi"],
                "temperature": env["temperature"],
                "humidity": env["humidity"],
                "primary_complaint_codes": ",".join(obs["primary_complaint_codes"])
            })
        observations_df = pd.DataFrame(observations_data)
        observations_df = observations_df.drop(columns=["environmental_context"])
        observations_df.to_csv(output_dir / "observations.csv", index=False)
        
        print(f"Saved CSV files to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic data for FestSafe AI")
    parser.add_argument("--hospitals", type=int, default=50, help="Number of hospitals")
    parser.add_argument("--events", type=int, default=10, help="Number of events")
    parser.add_argument("--days", type=int, default=90, help="Days of historical data")
    parser.add_argument("--output-dir", type=str, default="data/synthetic", help="Output directory")
    parser.add_argument("--format", choices=["json", "csv", "both"], default="both", help="Output format")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    simulator = DataSimulator(seed=args.seed)
    output_dir = Path(args.output_dir)
    
    print("Generating hospitals...")
    hospitals = simulator.generate_hospitals(args.hospitals)
    
    print("Generating events...")
    start_date = datetime.now() - timedelta(days=args.days)
    events = simulator.generate_events(args.events, start_date, days_ahead=args.days)
    
    print("Generating observations...")
    observations = simulator.generate_observations(
        hospitals, 
        start_date, 
        days=args.days,
        interval_hours=1
    )
    
    if args.format in ["json", "both"]:
        simulator.save_to_json(output_dir)
    
    if args.format in ["csv", "both"]:
        simulator.save_to_csv(output_dir)
    
    print("Data generation complete!")


if __name__ == "__main__":
    main()


