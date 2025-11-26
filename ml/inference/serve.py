"""
Model inference service for FestSafe AI.
"""

import os
import pickle
import joblib
import torch
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import mlflow
import mlflow.pytorch
import mlflow.sklearn


class ModelInferenceService:
    """Service for model inference."""
    
    def __init__(self, model_path: Optional[str] = None, model_type: str = "tabular"):
        """
        Args:
            model_path: Path to saved model or MLflow run ID
            model_type: "tabular" or "nn"
        """
        self.model_type = model_type
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load model from path or MLflow."""
        if model_path.startswith("mlflow://"):
            # Load from MLflow
            run_id = model_path.replace("mlflow://", "")
            if self.model_type == "tabular":
                self.model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")
            else:
                self.model = mlflow.pytorch.load_model(f"runs:/{run_id}/model")
        else:
            # Load from file
            if self.model_type == "tabular":
                self.model = joblib.load(model_path)
            else:
                self.model = torch.load(model_path, map_location=self.device)
                self.model.eval()
    
    def predict(
        self,
        features: np.ndarray,
        return_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Make predictions.
        
        Args:
            features: Input features (batch, sequence_length, feature_dim) for NN
                     or (batch, flattened_features) for tabular
            return_confidence: Whether to return confidence intervals
        
        Returns:
            Dictionary with predictions and optional confidence
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if self.model_type == "tabular":
            # Flatten if needed
            if len(features.shape) > 2:
                features = features.reshape(features.shape[0], -1)
            
            predictions = self.model.predict(features)
            
            # Simple confidence based on prediction variance
            if return_confidence:
                # For ensemble or uncertainty estimation, use prediction intervals
                # Here we use a simple heuristic
                confidence = np.ones_like(predictions) * 0.8  # Placeholder
            else:
                confidence = None
        else:
            # Neural network
            with torch.no_grad():
                features_tensor = torch.FloatTensor(features).to(self.device)
                predictions = self.model(features_tensor).cpu().numpy().flatten()
            
            if return_confidence:
                # Placeholder confidence
                confidence = np.ones_like(predictions) * 0.75
            else:
                confidence = None
        
        result = {
            "predictions": predictions.tolist(),
            "model_type": self.model_type
        }
        
        if confidence is not None:
            result["confidence"] = confidence.tolist()
        
        return result
    
    def predict_surge_risk(
        self,
        features: np.ndarray,
        threshold_low: float = 5.0,
        threshold_high: float = 15.0
    ) -> Dict[str, Any]:
        """
        Predict surge risk category.
        
        Args:
            features: Input features
            threshold_low: Threshold for low risk
            threshold_high: Threshold for high risk
        
        Returns:
            Risk category and details
        """
        pred_result = self.predict(features, return_confidence=True)
        predictions = np.array(pred_result["predictions"])
        
        risk_categories = []
        for pred in predictions:
            if pred < threshold_low:
                risk_categories.append("low")
            elif pred < threshold_high:
                risk_categories.append("medium")
            else:
                risk_categories.append("high")
        
        return {
            "risk_categories": risk_categories,
            "predictions": pred_result["predictions"],
            "confidence": pred_result.get("confidence", []),
            "thresholds": {
                "low": threshold_low,
                "high": threshold_high
            }
        }


# Singleton instance
_inference_service: Optional[ModelInferenceService] = None


def get_inference_service() -> ModelInferenceService:
    """Get or create inference service singleton."""
    global _inference_service
    
    if _inference_service is None:
        model_path = os.getenv("MODEL_PATH", "models/baseline_model.pkl")
        model_type = os.getenv("MODEL_TYPE", "tabular")
        _inference_service = ModelInferenceService(model_path, model_type)
    
    return _inference_service


