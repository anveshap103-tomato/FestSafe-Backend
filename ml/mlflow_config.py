"""
MLflow configuration for FestSafe AI.
"""

import mlflow
import os

# MLflow tracking URI
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Experiment name
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT", "festsafe-forecast")

# Create experiment if it doesn't exist
try:
    mlflow.create_experiment(EXPERIMENT_NAME)
except:
    pass  # Experiment already exists

mlflow.set_experiment(EXPERIMENT_NAME)


