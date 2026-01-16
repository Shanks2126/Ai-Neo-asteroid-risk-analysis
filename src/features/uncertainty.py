"""
Uncertainty quantification for model predictions.
Provides confidence intervals and model disagreement metrics.
"""

import numpy as np
from typing import Tuple, Optional


def calculate_uncertainty(
    model,
    input_scaled: np.ndarray,
    method: str = "ensemble_std"
) -> Tuple[float, float, float]:
    """
    Calculate prediction uncertainty using ensemble disagreement.
    
    Args:
        model: Trained RandomForest model
        input_scaled: Scaled input features
        method: Uncertainty method ('ensemble_std' or 'entropy')
        
    Returns:
        Tuple of (lower_bound, upper_bound, uncertainty_score)
    """
    if model is None:
        # No model, return high uncertainty
        return 0.0, 1.0, 0.5
    
    if not hasattr(model, 'estimators_'):
        # Not an ensemble model
        return 0.0, 1.0, 0.3
    
    if method == "ensemble_std":
        # Get predictions from each tree in the forest
        predictions = []
        for tree in model.estimators_:
            pred_proba = tree.predict_proba(input_scaled)[0]
            predictions.append(np.max(pred_proba))
        
        predictions = np.array(predictions)
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        
        # Uncertainty is the standard deviation of predictions
        uncertainty = std_pred
        
        # Confidence interval
        lower = max(0, mean_pred - 2 * std_pred)
        upper = min(1, mean_pred + 2 * std_pred)
        
        return lower, upper, uncertainty
    
    elif method == "entropy":
        # Entropy-based uncertainty
        proba = model.predict_proba(input_scaled)[0]
        
        # Calculate entropy
        entropy = -np.sum(proba * np.log(proba + 1e-10))
        max_entropy = np.log(len(proba))  # Maximum possible entropy
        
        uncertainty = entropy / max_entropy  # Normalized uncertainty
        
        mean_pred = np.max(proba)
        margin = uncertainty * 0.3  # Scale margin based on uncertainty
        
        lower = max(0, mean_pred - margin)
        upper = min(1, mean_pred + margin)
        
        return lower, upper, uncertainty
    
    else:
        raise ValueError(f"Unknown uncertainty method: {method}")


def get_confidence_level(uncertainty: float) -> str:
    """
    Convert uncertainty score to human-readable confidence level.
    
    Args:
        uncertainty: Uncertainty score (0-1, higher = more uncertain)
        
    Returns:
        Confidence level string
    """
    if uncertainty < 0.1:
        return "Very High"
    elif uncertainty < 0.2:
        return "High"
    elif uncertainty < 0.35:
        return "Moderate"
    elif uncertainty < 0.5:
        return "Low"
    else:
        return "Very Low"
