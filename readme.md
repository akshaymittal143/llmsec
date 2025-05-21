# LLMSec: LLM-Based Security Validation Framework

Enterprise-grade security validation framework for Infrastructure-as-Code using Large Language Models.

## Features
- 🔒 Real-time security policy validation
- 🚀 CI/CD pipeline integration (Jenkins, GitHub Actions)
- 🤖 Multi-LLM ensemble validation
- 📊 Confidence-based decision making
- 🛡️ Privacy-preserving local deployment
- 📈 Comprehensive metrics and monitoring

## Requirements
- Python 3.8+
- NVIDIA GPU with 40GB+ VRAM (for local LLM deployment)
- PyTorch 2.1
- Langchain 0.1.0
- CUDA 11.8+ (for GPU support)

## Quick Start

```bash
# Clone repository
git clone https://github.com/akshaymittal143/llmsec.git
cd llmsec

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run test suite
python scripts/run_tests.py

# Validate a specific configuration
python scripts/validate_config.py --config examples/kubernetes/deployment.yaml
```

## Test Suite Coverage
- **500+ Synthetic Test Cases**
  - Kubernetes (300 cases)
    - Pod Security Policies
    - Network Policies
    - RBAC Configurations
  - IAM Policies (200 cases)
    - AWS IAM
    - Azure RBAC
    - GCP IAM
  - Infrastructure Configs
    - Terraform
    - CloudFormation
    - Helm Charts

## Configuration

### Model Settings
```yaml
# configs/models/config.yaml
models:
  gpt4:
    version: "gpt-4-0314"
    temperature: 0.1
    max_tokens: 500
  codellama:
    model_path: "codellama-7b-hf"
    quantization: "4bit"
```

### Prompt Templates
See `configs/prompts/` for examples of:
- Security policy validation
- Compliance checking
- Risk assessment
- Remediation suggestions

## Metrics & Monitoring
- **Performance Metrics**
  - F1 Score: 0.95 (target)
  - Expected Calibration Error (ECE): <0.1
  - Risk Score (α=1, β=5)
  - Latency: <3.1s per check
- **Operational Metrics**
  - False Positive Rate: <10%
  - Manual Review Rate: <20%
  - Pipeline Impact: <5s added to CI/CD

## Jenkins Integration

```groovy
// Jenkinsfile example
stage('Security Validation') {
    steps {
        script {
            def result = sh(
                script: '''
                    python3 scripts/validate_config.py \
                        --config ${WORKSPACE}/k8s/deployment.yaml \
                        --threshold 0.8
                ''',
                returnStdout: true
            )
            if (result.contains("HIGH_RISK")) {
                error "Security validation failed"
            }
        }
    }
}
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
MIT License - see [LICENSE](LICENSE) for details.

## Citation
```bibtex
@inproceedings{mittal2025llmsec,
    author = {Mittal, Akshay},
    title = {Practical Integration of Large Language Models into Enterprise CI/CD Pipelines for Security Policy Validation},
    booktitle = {Proc. IEEE CISOSE},
    year = {2025}
}
```