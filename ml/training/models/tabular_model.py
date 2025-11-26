"""
Tabular models for hospital forecasting.
"""

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from typing import Dict, Any, Tuple


class TabularForecastModel:
    """Gradient-boosted tree model for hospital forecasting."""
    
    def __init__(self, model_type: str = "gradient_boosting", **kwargs):
        """
        Args:
            model_type: "gradient_boosting" or "random_forest"
            **kwargs: Model hyperparameters
        """
        if model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(
                n_estimators=kwargs.get("n_estimators", 100),
                max_depth=kwargs.get("max_depth", 5),
                learning_rate=kwargs.get("learning_rate", 0.1),
                random_state=kwargs.get("random_state", 42)
            )
        elif model_type == "random_forest":
            self.model = RandomForestRegressor(
                n_estimators=kwargs.get("n_estimators", 100),
                max_depth=kwargs.get("max_depth", 10),
                random_state=kwargs.get("random_state", 42)
            )
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the model."""
        # Flatten sequences for tabular model
        if len(X_train.shape) > 2:
            X_train = X_train.reshape(X_train.shape[0], -1)
        
        self.model.fit(X_train, y_train)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if len(X.shape) > 2:
            X = X.reshape(X.shape[0], -1)
        return self.model.predict(X)
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate the model."""
        y_pred = self.predict(X_test)
        
        return {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred)
        }
    
    def save(self, path: str):
        """Save the model."""
        joblib.dump(self.model, path)
    
    def load(self, path: str):
        """Load the model."""
        self.model = joblib.load(path)


