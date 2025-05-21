from typing import Dict, List, Optional, Type
import asyncio
import time
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from concurrent.futures import ThreadPoolExecutor
from ..utils.exceptions import ModelError, ModelTimeoutError
from ..utils.caching import cache_result
from ..utils.metrics import ValidationVerdict

logger = logging.getLogger(__name__)

@dataclass
class ModelPrediction:
    """Structured prediction from a single model."""
    verdict: ValidationVerdict
    confidence: float
    violations: List[str]
    latency_ms: int
    metadata: Dict

    def __post_init__(self):
        """Validate prediction data."""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        if self.latency_ms < 0:
            raise ValueError(f"Latency cannot be negative, got {self.latency_ms}")

class BaseModel(ABC):
    """Abstract base class for LLM models."""
    @abstractmethod
    async def predict(self, config: Dict) -> ModelPrediction:
        """Generate prediction for given configuration."""
        pass

    @abstractmethod
    async def generate_remediation(self, violations: List[str]) -> List[str]:
        """Generate remediation steps for violations."""
        pass

class ModelRegistry:
    """Registry of available model implementations."""
    _models: Dict[str, Type[BaseModel]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(model_cls: Type[BaseModel]):
            cls._models[name] = model_cls
            return model_cls
        return decorator

    @classmethod
    def get_model(cls, name: str) -> Type[BaseModel]:
        if name not in cls._models:
            raise ValueError(f"Unknown model type: {name}")
        return cls._models[name]

class LLMEnsemble:
    """Ensemble of LLM models for security validation."""
    
    def __init__(self, config: Dict):
        self.models: List[BaseModel] = []
        self.last_latency: Optional[int] = None
        self.timeout = config.get("timeout_seconds", 30)
        
        # Initialize models from registry
        for model_name, model_config in config.get("models", {}).items():
            model_cls = ModelRegistry.get_model(model_name)
            self.models.append(model_cls(model_config))
            
        if not self.models:
            raise ValueError("No models configured for ensemble")

    @cache_result(ttl_seconds=3600)
    async def predict(self, config: Dict) -> List[ModelPrediction]:
        """Generate predictions from all models in parallel."""
        start_time = time.time()
        
        try:
            # Run predictions with timeout
            tasks = [
                asyncio.create_task(model.predict(config))
                for model in self.models
            ]
            
            done, pending = await asyncio.wait(
                tasks,
                timeout=self.timeout,
                return_when=asyncio.ALL_COMPLETED
            )
            
            # Cancel any pending tasks
            for task in pending:
                task.cancel()
            
            # Handle results
            predictions = []
            for task in done:
                try:
                    pred = await task
                    predictions.append(pred)
                except Exception as e:
                    logger.error(f"Model prediction failed: {str(e)}")
            
            if not predictions:
                raise ModelError("All models failed to generate predictions")
            
            self.last_latency = int((time.time() - start_time) * 1000)
            return predictions
            
        except asyncio.TimeoutError:
            raise ModelTimeoutError(f"Prediction timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"Ensemble prediction failed: {str(e)}")
            raise ModelError(str(e))