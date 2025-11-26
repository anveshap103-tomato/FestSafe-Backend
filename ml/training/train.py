"""
Training script for FestSafe AI models.
"""

import argparse
import yaml
import mlflow
import mlflow.pytorch
import mlflow.sklearn
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from sklearn.model_selection import train_test_split

from dataset import HospitalForecastDataset, load_data
from models.tabular_model import TabularForecastModel
from models.nn_model import LSTMForecastModel, train_epoch, evaluate


def train_tabular_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    config: dict
) -> TabularForecastModel:
    """Train a tabular model."""
    model = TabularForecastModel(
        model_type=config.get("model_type", "gradient_boosting"),
        **config.get("hyperparameters", {})
    )
    
    with mlflow.start_run(run_name="tabular_model"):
        # Log parameters
        mlflow.log_params(config.get("hyperparameters", {}))
        
        # Train
        model.train(X_train, y_train)
        
        # Evaluate
        train_metrics = model.evaluate(X_train, y_train)
        val_metrics = model.evaluate(X_val, y_val)
        
        # Log metrics
        for metric, value in train_metrics.items():
            mlflow.log_metric(f"train_{metric}", value)
        for metric, value in val_metrics.items():
            mlflow.log_metric(f"val_{metric}", value)
        
        # Log model
        mlflow.sklearn.log_model(model.model, "model")
        
        print(f"Validation MAE: {val_metrics['mae']:.2f}")
        print(f"Validation RMSE: {val_metrics['rmse']:.2f}")
        print(f"Validation R2: {val_metrics['r2']:.2f}")
    
    return model


def train_nn_model(
    train_dataset: HospitalForecastDataset,
    val_dataset: HospitalForecastDataset,
    config: dict,
    device: torch.device
) -> LSTMForecastModel:
    """Train a neural network model."""
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.get("batch_size", 32),
        shuffle=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.get("batch_size", 32),
        shuffle=False
    )
    
    # Get input size from first sample
    sample_features, _ = train_dataset[0]
    input_size = sample_features.shape[1]
    
    # Create model
    model = LSTMForecastModel(
        input_size=input_size,
        hidden_size=config.get("hidden_size", 64),
        num_layers=config.get("num_layers", 2),
        dropout=config.get("dropout", 0.2)
    ).to(device)
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config.get("learning_rate", 0.001)
    )
    
    with mlflow.start_run(run_name="lstm_model"):
        # Log parameters
        mlflow.log_params({
            "hidden_size": config.get("hidden_size", 64),
            "num_layers": config.get("num_layers", 2),
            "dropout": config.get("dropout", 0.2),
            "learning_rate": config.get("learning_rate", 0.001),
            "batch_size": config.get("batch_size", 32)
        })
        
        # Training loop
        num_epochs = config.get("num_epochs", 50)
        best_val_loss = float("inf")
        
        for epoch in range(num_epochs):
            train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
            val_metrics = evaluate(model, val_loader, criterion, device)
            
            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("val_loss", val_metrics["loss"], step=epoch)
            mlflow.log_metric("val_mae", val_metrics["mae"], step=epoch)
            mlflow.log_metric("val_rmse", val_metrics["rmse"], step=epoch)
            
            if val_metrics["loss"] < best_val_loss:
                best_val_loss = val_metrics["loss"]
                mlflow.pytorch.log_model(model, "model")
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{num_epochs}")
                print(f"  Train Loss: {train_loss:.4f}")
                print(f"  Val Loss: {val_metrics['loss']:.4f}")
                print(f"  Val MAE: {val_metrics['mae']:.2f}")
                print(f"  Val RMSE: {val_metrics['rmse']:.2f}")
    
    return model


def main():
    parser = argparse.ArgumentParser(description="Train FestSafe AI models")
    parser.add_argument("--config", type=str, required=True, help="Path to config YAML")
    parser.add_argument("--data-dir", type=str, default="data/synthetic", help="Data directory")
    parser.add_argument("--model-type", choices=["tabular", "nn", "both"], default="both")
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    
    # Set MLflow tracking URI
    mlflow.set_tracking_uri(config.get("mlflow_uri", "http://localhost:5000"))
    mlflow.set_experiment(config.get("experiment_name", "festsafe-forecast"))
    
    # Load data
    print("Loading data...")
    observations_df, hospitals_df, events_df = load_data(args.data_dir)
    
    # Create datasets
    print("Creating datasets...")
    full_dataset = HospitalForecastDataset(
        observations_df,
        hospitals_df,
        events_df,
        sequence_length=config.get("sequence_length", 24),
        forecast_horizon=config.get("forecast_horizon", 24)
    )
    
    # Split train/val
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        full_dataset,
        [train_size, val_size]
    )
    
    # Prepare data for tabular model
    X_train = np.array([train_dataset[i][0].numpy() for i in range(len(train_dataset))])
    y_train = np.array([train_dataset[i][1].item() for i in range(len(train_dataset))])
    X_val = np.array([val_dataset[i][0].numpy() for i in range(len(val_dataset))])
    y_val = np.array([val_dataset[i][1].item() for i in range(len(val_dataset))])
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Train models
    if args.model_type in ["tabular", "both"]:
        print("\nTraining tabular model...")
        tabular_config = config.get("tabular", {})
        train_tabular_model(X_train, y_train, X_val, y_val, tabular_config)
    
    if args.model_type in ["nn", "both"]:
        print("\nTraining neural network model...")
        nn_config = config.get("neural_network", {})
        train_nn_model(train_dataset, val_dataset, nn_config, device)
    
    print("\nTraining complete!")


if __name__ == "__main__":
    main()


