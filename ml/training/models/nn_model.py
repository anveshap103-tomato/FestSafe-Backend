"""
Neural network models for hospital forecasting.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
import numpy as np


class LSTMForecastModel(nn.Module):
    """LSTM-based model for time-series forecasting."""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
        output_size: int = 1
    ):
        super(LSTMForecastModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_size // 2, output_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        # x shape: (batch, sequence_length, features)
        lstm_out, _ = self.lstm(x)
        
        # Take the last output
        last_output = lstm_out[:, -1, :]
        
        # Fully connected layers
        out = self.fc1(last_output)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out


class HybridForecastModel(nn.Module):
    """Hybrid model: LSTM for time-series + MLP for static features."""
    
    def __init__(
        self,
        time_series_features: int,
        static_features: int,
        lstm_hidden: int = 64,
        mlp_hidden: int = 32,
        num_layers: int = 2,
        dropout: float = 0.2,
        output_size: int = 1
    ):
        super(HybridForecastModel, self).__init__()
        
        # Time-series encoder (LSTM)
        self.lstm = nn.LSTM(
            input_size=time_series_features,
            hidden_size=lstm_hidden,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Static features encoder (MLP)
        self.static_encoder = nn.Sequential(
            nn.Linear(static_features, mlp_hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(mlp_hidden, mlp_hidden // 2)
        )
        
        # Fusion and output
        combined_size = lstm_hidden + mlp_hidden // 2
        self.fusion = nn.Sequential(
            nn.Linear(combined_size, combined_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(combined_size // 2, output_size)
        )
    
    def forward(
        self,
        time_series: torch.Tensor,
        static_features: torch.Tensor
    ) -> torch.Tensor:
        """Forward pass."""
        # Time-series encoding
        lstm_out, _ = self.lstm(time_series)
        time_encoded = lstm_out[:, -1, :]  # Last timestep
        
        # Static features encoding
        static_encoded = self.static_encoder(static_features)
        
        # Concatenate and fuse
        combined = torch.cat([time_encoded, static_encoded], dim=1)
        output = self.fusion(combined)
        
        return output


def train_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device
) -> float:
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    
    for features, targets in dataloader:
        features = features.to(device)
        targets = targets.to(device)
        
        optimizer.zero_grad()
        outputs = model(features)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)


def evaluate(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> Dict[str, float]:
    """Evaluate the model."""
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for features, targets in dataloader:
            features = features.to(device)
            targets = targets.to(device)
            
            outputs = model(features)
            loss = criterion(outputs, targets)
            
            total_loss += loss.item()
            all_preds.extend(outputs.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
    
    all_preds = np.array(all_preds).flatten()
    all_targets = np.array(all_targets).flatten()
    
    mae = np.mean(np.abs(all_preds - all_targets))
    rmse = np.sqrt(np.mean((all_preds - all_targets) ** 2))
    
    return {
        "loss": total_loss / len(dataloader),
        "mae": mae,
        "rmse": rmse
    }


