"""
Dataset classes for ML training.
"""

from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from torch.utils.data import Dataset
import torch


class HospitalForecastDataset(Dataset):
    """Dataset for hospital forecast prediction."""
    
    def __init__(
        self,
        observations_df: pd.DataFrame,
        hospitals_df: pd.DataFrame,
        events_df: pd.DataFrame,
        sequence_length: int = 24,
        forecast_horizon: int = 24,
        target_col: str = "new_arrivals"
    ):
        """
        Args:
            observations_df: Time-series observations
            hospitals_df: Hospital metadata
            events_df: Event data
            sequence_length: Number of historical hours to use
            forecast_horizon: Hours ahead to forecast
            target_col: Column to predict
        """
        self.sequence_length = sequence_length
        self.forecast_horizon = forecast_horizon
        self.target_col = target_col
        
        # Merge data
        self.data = self._prepare_data(observations_df, hospitals_df, events_df)
        self.sequences = self._create_sequences()
    
    def _prepare_data(
        self,
        observations_df: pd.DataFrame,
        hospitals_df: pd.DataFrame,
        events_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Prepare and merge all data sources."""
        # Convert timestamps
        observations_df["timestamp"] = pd.to_datetime(observations_df["timestamp"])
        events_df["start_ts"] = pd.to_datetime(events_df["start_ts"])
        events_df["end_ts"] = pd.to_datetime(events_df["end_ts"])
        
        # Merge hospital features
        df = observations_df.merge(
            hospitals_df[["id", "bed_count", "icu_count", "oxygen_capacity", "doctors", "nurses"]],
            left_on="hospital_id",
            right_on="id",
            how="left"
        )
        df = df.drop(columns=["id"])
        
        # Add event features
        df["event_attendance"] = 0
        df["event_distance"] = 0
        
        for _, event in events_df.iterrows():
            mask = (df["timestamp"] >= event["start_ts"]) & (df["timestamp"] <= event["end_ts"])
            if mask.any():
                # Calculate distance (simplified)
                df.loc[mask, "event_attendance"] = event["expected_attendance"]
                # Distance calculation would go here
        
        # Sort by timestamp
        df = df.sort_values(["hospital_id", "timestamp"]).reset_index(drop=True)
        
        return df
    
    def _create_sequences(self) -> List[Dict]:
        """Create sequences for training."""
        sequences = []
        
        for hospital_id in self.data["hospital_id"].unique():
            hospital_data = self.data[self.data["hospital_id"] == hospital_id].copy()
            
            if len(hospital_data) < self.sequence_length + self.forecast_horizon:
                continue
            
            # Feature columns
            feature_cols = [
                "new_arrivals", "current_patients", "avg_age",
                "aqi", "temperature", "humidity",
                "bed_count", "icu_count", "oxygen_capacity",
                "doctors", "nurses", "event_attendance"
            ]
            
            for i in range(len(hospital_data) - self.sequence_length - self.forecast_horizon):
                # Historical sequence
                seq_data = hospital_data.iloc[i:i + self.sequence_length]
                features = seq_data[feature_cols].values.astype(np.float32)
                
                # Target (future value)
                target_idx = i + self.sequence_length + self.forecast_horizon - 1
                target = hospital_data.iloc[target_idx][self.target_col]
                
                sequences.append({
                    "features": features,
                    "target": float(target),
                    "hospital_id": hospital_id,
                    "timestamp": hospital_data.iloc[i + self.sequence_length]["timestamp"]
                })
        
        return sequences
    
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get a single sequence."""
        seq = self.sequences[idx]
        features = torch.FloatTensor(seq["features"])
        target = torch.FloatTensor([seq["target"]])
        
        return features, target


def load_data(data_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load data from CSV files."""
    observations_df = pd.read_csv(f"{data_dir}/observations.csv")
    hospitals_df = pd.read_csv(f"{data_dir}/hospitals.csv")
    events_df = pd.read_csv(f"{data_dir}/events.csv")
    
    return observations_df, hospitals_df, events_df


