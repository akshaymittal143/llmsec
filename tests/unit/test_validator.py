import pytest
from src.core.validator import SecurityValidator
from pathlib import Path
import yaml

@pytest.fixture
def validator():
    config_path = Path(__file__).parent / "../../configs/models/config.yaml"
    return SecurityValidator(config_path)

@pytest.fixture
def test_cases():
    test_path = Path(__file__).parent / "../../test_cases/kubernetes"
    cases = {}
    for yaml_file in test_path.glob("*.yaml"):
        with open(yaml_file) as f:
            cases[yaml_file.stem] = yaml.safe_load(f)
    return cases

def test_privileged_container_detection(validator):
    """Test detection of privileged container security issue."""
    yaml_content = """
    apiVersion: v1
    kind: Pod
    spec:
      containers:
      - name: nginx
        securityContext:
          privileged: true
    """
    result = validator.validate_config(yaml_content)
    assert result["verdict"] == "INSECURE"
    assert any("privileged container" in v.lower() for v in result["violations"])
    assert result["confidence"] > 0.8
    assert result["latency_ms"] < 3500  # Performance SLA

def test_secure_configuration_passes(validator):
    """Test that secure configuration passes validation."""
    yaml_content = """
    apiVersion: v1
    kind: Pod
    spec:
      containers:
      - name: nginx
        securityContext:
          runAsNonRoot: true
          allowPrivilegeEscalation: false
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
    """
    result = validator.validate_config(yaml_content)
    assert result["verdict"] == "SECURE"
    assert len(result["violations"]) == 0
    assert result["confidence"] > 0.9

def test_missing_resource_limits(validator):
    """Test detection of missing resource limits."""
    yaml_content = """
    apiVersion: v1
    kind: Pod
    spec:
      containers:
      - name: nginx
        image: nginx:latest  # Also a security issue: latest tag
    """
    result = validator.validate_config(yaml_content)
    assert result["verdict"] == "INSECURE"
    assert any("resource limits" in v.lower() for v in result["violations"])
    assert any("latest tag" in v.lower() for v in result["violations"])

def test_remediation_suggestions(validator):
    """Test that remediation suggestions are provided."""
    yaml_content = """
    apiVersion: v1
    kind: Pod
    spec:
      containers:
      - name: nginx
        securityContext:
          privileged: true
    """
    result = validator.validate_config(yaml_content)
    assert len(result["remediation"]) > 0
    assert any("privileged: false" in r for r in result["remediation"])

@pytest.mark.parametrize("confidence_threshold", [0.7, 0.8, 0.9])
def test_confidence_thresholds(validator, confidence_threshold):
    """Test different confidence thresholds."""
    validator.confidence_threshold = confidence_threshold
    yaml_content = """
    apiVersion: v1
    kind: Pod
    spec:
      containers:
      - name: nginx
        securityContext:
          runAsNonRoot: true
    """
    result = validator.validate_config(yaml_content)
    assert result["confidence"] >= confidence_threshold

def test_malformed_yaml(validator):
    """Test handling of malformed YAML."""
    yaml_content = """
    invalid:
      - yaml:
          content:
            - missing
              indentation
    """
    with pytest.raises(yaml.YAMLError):
        validator.validate_config(yaml_content)

def test_ensemble_agreement(validator):
    """Test ensemble model agreement metrics."""
    yaml_content = """
    apiVersion: v1
    kind: Pod
    spec:
      containers:
      - name: nginx
        securityContext:
          privileged: true
    """
    result = validator.validate_config(yaml_content)
    assert "model_agreement" in result
    assert 0 <= result["model_agreement"] <= 1.0