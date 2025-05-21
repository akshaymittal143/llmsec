# LLMSec: LLM-Based Security Validation Framework

Enterprise-grade security validation framework for Infrastructure-as-Code using Large Language Models, designed for production CI/CD pipelines.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Key Features
- 🔒 **Real-time Security Validation**
  - F1 Score: 0.95 on CIS Benchmark tests
  - Latency: <3.1s per validation
  - Privacy-preserving local deployment
- 🚀 **CI/CD Integration**
  - Jenkins pipeline support
  - GitHub Actions workflows
  - GitLab CI integration
- 🤖 **Advanced LLM Features**
  - Multi-model ensemble validation
  - Confidence-based decisioning
  - Automated remediation suggestions

## System Requirements

### Hardware
- CPU: 8+ cores recommended
- RAM: 16GB minimum, 32GB recommended
- GPU: NVIDIA GPU with 40GB+ VRAM (for local LLM deployment)
  - Tested on: A100, A6000, V100

### Software
- Python 3.8+
- CUDA 11.8+ and cuDNN 8.6+
- Docker 20.10+ (optional)
- Dependencies:
  - PyTorch 2.1+
  - Langchain 0.1.0
  - transformers 4.34+
  - See requirements.txt for full list

## Quick Start Guide

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/akshaymittal143/llmsec.git
cd llmsec

# Set up Python environment (Mac/Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up pre-commit hooks
pre-commit install

# Run test suite
make test

# Run single validation
python scripts/validate_config.py \
    --config examples/kubernetes/deployment.yaml \
    --threshold 0.8
```

### Docker Deployment
```bash
# Build container
docker build -t llmsec:latest .

# Run validation
docker run --gpus all -v $(pwd)/configs:/app/configs llmsec:latest \
    validate --config /app/configs/deployment.yaml
```

## Architecture

### Components
```
llmsec/
├── src/
│   ├── core/          # Core validation logic
│   ├── models/        # LLM implementations
│   ├── validation/    # Policy validators
│   └── utils/         # Helper utilities
├── configs/           # Configuration files
├── test_cases/        # Test suite
└── scripts/           # CLI tools
```

### Supported Models
- OpenAI GPT-4 (API)
- Code-Llama 7B/13B (local deployment)
- Custom fine-tuned models
- Ensemble combinations

## Security Validation Coverage

### Infrastructure Configurations
- **Kubernetes** (300+ test cases)
  - Pod Security Policies
  - Network Policies
  - RBAC/ServiceAccounts
  - Resource Quotas
  - PodDisruptionBudgets

- **Cloud IAM** (200+ test cases)
  - AWS IAM Policies
  - Azure RBAC
  - GCP IAM
  - Cross-account access

- **Infrastructure Templates**
  - Terraform modules
  - CloudFormation
  - Helm charts
  - Ansible playbooks

## Metrics & Monitoring

### Performance Metrics
| Metric | Target | Description |
|--------|--------|-------------|
| F1 Score | ≥0.95 | Overall accuracy |
| ECE | <0.1 | Calibration error |
| Latency | <3.1s | Per-check time |
| FP Rate | <10% | False positive rate |

### Operational Metrics
- Pipeline Impact: <5s added to CI/CD
- Manual Review Rate: <20%
- Model Agreement: >80%

## Contributing
We welcome contributions! Please see:
- [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community standards
- [SECURITY.md](SECURITY.md) for security policy

## License
MIT License - see [LICENSE](LICENSE)
