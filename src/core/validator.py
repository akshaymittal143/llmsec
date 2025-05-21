from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import yaml
import logging
import time
from ..models import LLMEnsemble
from ..utils.metrics import calculate_confidence
from ..utils.exceptions import ValidationError, ModelError

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    verdict: str
    confidence: float
    violations: List[str]
    remediation: List[str]
    latency_ms: int
    model_agreement: float
    raw_predictions: List[Dict]

class SecurityValidator:
    """
    Core security validation engine using LLM ensemble.
    
    Features:
    - Multi-model validation
    - Confidence-based decisions
    - Automated remediation suggestions
    - Caching for performance
    """
    
    def __init__(self, config_path: str):
        """Initialize validator with configuration."""
        try:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
            self.ensemble = LLMEnsemble(self.config["models"])
            self.confidence_threshold = self.config.get("confidence_threshold", 0.8)
            self.max_latency = self.config.get("max_latency_ms", 3500)
            self._setup_logging()
        except Exception as e:
            logger.error(f"Failed to initialize validator: {str(e)}")
            raise

    def _setup_logging(self):
        """Configure logging with appropriate handlers and formatters."""
        log_config = self.config.get("logging", {})
        logging.basicConfig(
            level=log_config.get("level", "INFO"),
            format=log_config.get("format", '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )

    def validate_config(self, yaml_content: str) -> ValidationResult:
        """
        Validate configuration using LLM ensemble.
        
        Args:
            yaml_content: YAML configuration to validate
            
        Returns:
            ValidationResult containing verdict, confidence, violations, etc.
            
        Raises:
            ValidationError: If validation fails
            ModelError: If LLM ensemble fails
            yaml.YAMLError: If YAML parsing fails
        """
        start_time = time.time()
        try:
            # Parse YAML
            config = yaml.safe_load(yaml_content)
            
            # Get ensemble predictions
            predictions = self.ensemble.predict(config)
            
            # Calculate confidence and agreement
            verdict, confidence = calculate_confidence(predictions)
            model_agreement = self._calculate_agreement(predictions)
            
            # Performance check
            latency = int((time.time() - start_time) * 1000)
            if latency > self.max_latency:
                logger.warning(f"Validation exceeded latency threshold: {latency}ms")
            
            # Get violations and remediation
            violations = self._extract_violations(predictions)
            remediation = self._generate_remediation(violations)
            
            return ValidationResult(
                verdict=verdict,
                confidence=confidence,
                violations=violations,
                remediation=remediation,
                latency_ms=latency,
                model_agreement=model_agreement,
                raw_predictions=predictions
            )
            
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML content: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise ValidationError(str(e))

    def _extract_violations(self, predictions: List[Dict]) -> List[str]:
        """Extract security violations from model predictions."""
        violations = set()
        for pred in predictions:
            if pred.get("violations"):
                violations.update(pred["violations"])
        return sorted(list(violations))
        
    def _generate_remediation(self, violations: List[str]) -> List[str]:
        """Generate remediation steps for identified violations."""
        return self.ensemble.generate_remediation(violations)

    def _calculate_agreement(self, predictions: List[Dict]) -> float:
        """Calculate agreement score between ensemble models."""
        if not predictions:
            return 0.0
        verdicts = [p.get("verdict") for p in predictions]
        majority = max(set(verdicts), key=verdicts.count)
        return verdicts.count(majority) / len(verdicts)