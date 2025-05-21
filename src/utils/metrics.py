from typing import List, Dict, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum, auto
import time
import logging

logger = logging.getLogger(__name__)

class ValidationVerdict(Enum):
    """Standardize validation verdicts."""
    SECURE = auto()
    INSECURE = auto()
    UNKNOWN = auto()

@dataclass
class MetricsResult:
    """Container for validation metrics."""
    f1_score: float
    precision: float
    recall: float
    ece: float  # Expected Calibration Error
    latency_p95: float
    model_agreement: float
    sample_count: int
    timestamp: float = time.time()

    def __post_init__(self):
        """Validate metric values."""
        if not 0 <= self.f1_score <= 1:
            raise ValueError(f"F1 score must be between 0 and 1, got {self.f1_score}")
        if not 0 <= self.model_agreement <= 1:
            raise ValueError(f"Model agreement must be between 0 and 1")

def calculate_confidence(predictions: List[Dict]) -> Tuple[ValidationVerdict, float]:
    """Calculate ensemble verdict and confidence."""
    if not predictions:
        raise ValueError("No predictions provided")
    
    try:
        # Get verdicts and confidences
        verdicts = [ValidationVerdict[p.verdict] for p in predictions]
        confidences = np.array([float(p.confidence) for p in predictions])
        
        # Validate confidence values
        if not np.all((0 <= confidences) & (confidences <= 1)):
            raise ValueError("Confidence values must be between 0 and 1")
        
        # Calculate majority verdict
        verdict_counts = {}
        for v in verdicts:
            verdict_counts[v] = verdict_counts.get(v, 0) + 1
        
        majority_verdict = max(verdict_counts.items(), key=lambda x: x[1])[0]
        
        # Calculate agreement-weighted confidence
        agreement = verdict_counts[majority_verdict] / len(verdicts)
        confidence = float(np.mean(confidences) * agreement)
        
        return majority_verdict, confidence
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error calculating confidence: {str(e)}")
        return ValidationVerdict.UNKNOWN, 0.0

def calculate_metrics(results: List[Dict], ground_truth: Dict) -> MetricsResult:
    """
    Calculate comprehensive validation metrics.
    
    Args:
        results: List of validation results
        ground_truth: Ground truth labels
        
    Returns:
        MetricsResult with computed metrics
    """
    # Calculate basic metrics
    tp = fp = fn = 0
    latencies = []
    
    for result in results:
        pred = result["verdict"] == "INSECURE"
        true = ground_truth[result["id"]] == "INSECURE"
        
        if pred and true:
            tp += 1
        elif pred and not true:
            fp += 1
        elif not pred and true:
            fn += 1
            
        latencies.append(result["latency_ms"])
    
    # Calculate F1, precision, recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Calculate ECE
    ece = calculate_ece(results, ground_truth)
    
    # Calculate latency percentile
    latency_p95 = float(np.percentile(latencies, 95))
    
    # Calculate model agreement
    agreements = [r["model_agreement"] for r in results]
    avg_agreement = float(np.mean(agreements))
    
    return MetricsResult(
        f1_score=f1,
        precision=precision,
        recall=recall,
        ece=ece,
        latency_p95=latency_p95,
        model_agreement=avg_agreement,
        sample_count=len(results)
    )

def calculate_ece(results: List[Dict], ground_truth: Dict, bins: int = 10) -> float:
    """Calculate Expected Calibration Error."""
    confidences = np.array([r["confidence"] for r in results])
    correct = np.array([
        r["verdict"] == ground_truth[r["id"]] for r in results
    ])
    
    bin_boundaries = np.linspace(0, 1, bins + 1)
    bin_indices = np.digitize(confidences, bin_boundaries) - 1
    
    ece = 0.0
    for bin_idx in range(bins):
        bin_mask = bin_indices == bin_idx
        if not any(bin_mask):
            continue
            
        bin_conf = confidences[bin_mask].mean()
        bin_acc = correct[bin_mask].mean()
        bin_size = bin_mask.sum()
        
        ece += (bin_size / len(results)) * abs(bin_conf - bin_acc)
    
    return float(ece)