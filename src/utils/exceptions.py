class LLMSecError(Exception):
    """Base exception for all LLMSec errors."""
    pass

class ValidationError(LLMSecError):
    """Raised when validation fails."""
    pass

class ModelError(LLMSecError):
    """Raised when model operations fail."""
    pass

class ModelTimeoutError(ModelError):
    """Raised when model operation times out."""
    pass

class ConfigurationError(LLMSecError):
    """Raised for configuration issues."""
    pass