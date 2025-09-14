# 🛡️ Code Guardian(a side hustle project, built over weekend, i might maintain it 🤓)

---

## 🚨 The Problem

**60% of organizations don't evaluate AI-generated code for vulnerabilities.** With AI coding tools becoming ubiquitous, developers are unknowingly introducing security flaws, performance bottlenecks, and maintainability issues into production systems.

Research shows that **AI makes experienced developers 19% slower** while they *think* it's making them 20% faster. The gap between perception and reality is dangerous.

> 💡 **"Even GitHub's own security scanning flagged our intentionally vulnerable examples during development - proving that security tools like Code Guardian are essential!"**

## ✨ The Solution

Code Guardian fills this critical gap by providing comprehensive analysis of AI-generated code:

- 🔐 **Security Scanner** - Detects AI-specific vulnerabilities and common security flaws
- ⚡ **Performance Analyzer** - Identifies inefficient patterns AI often creates
- 🧹 **Maintainability Scorer** - Rates code quality and readability
- 🤖 **AI Pattern Detector** - Recognizes AI-generated code with confidence scoring
- 📊 **Rich Reporting** - Beautiful HTML/JSON/CLI reports with actionable insights

## 🎯 Quick Start

### Installation

```bash
pip install codeGuardian
```

### Basic Usage

```bash
# Scan current directory
ai-guardian scan .

# Scan specific files with custom config
ai-guardian scan src/ --config .ai-guardian.yml --format html

# Initialize configuration
ai-guardian init .
```

### Example Output

```
🛡️ Code Guardian Report

📊 Analysis Results
┌─────────────────────────┬───────┬────────┐
│ Metric                  │ Value │ Status │
├─────────────────────────┼───────┼────────┤
│ Files Scanned          │   42  │   ℹ️    │
│ Security Issues        │    7  │   🔴   │
│ Performance Issues     │   12  │   🟡   │
│ Maintainability Score  │  6.8  │   🟡   │
│ AI Generated Code      │ 73.2% │   ℹ️    │
└─────────────────────────┴───────┴────────┘

🚨 Critical Issues Found:
● CRITICAL: Hardcoded API key detected (auth.py:15)
● HIGH: SQL injection via string formatting (database.py:42)
● HIGH: Unsafe pickle deserialization (models.py:28)
```

## 🔥 Key Features

### 🔐 Security Analysis
- **SQL Injection Detection** - Identifies vulnerable query patterns
- **XSS Prevention** - Catches unsafe DOM manipulation
- **Hardcoded Secrets** - Detects API keys, passwords, tokens
- **Unsafe Deserialization** - Finds pickle/yaml vulnerabilities
- **Command Injection** - Spots dangerous system calls

### ⚡ Performance Analysis
- **Complexity Scoring** - Cyclomatic complexity analysis
- **Loop Efficiency** - Detects inefficient iteration patterns
- **Memory Usage** - Identifies memory-intensive operations
- **Database Optimization** - Finds N+1 queries and similar issues
- **Algorithm Analysis** - Suggests more efficient approaches

### 🤖 AI Detection Engine
- **Pattern Recognition** - Identifies AI-generated code signatures
- **Confidence Scoring** - Quantifies likelihood of AI generation
- **Comment Analysis** - Detects AI-style explanatory comments
- **Naming Conventions** - Spots generic AI variable/function names
- **Code Structure** - Recognizes AI coding patterns

### 📊 Beautiful Reports
- **CLI Dashboard** - Rich terminal output with colors and tables
- **HTML Reports** - Professional web-based reports
- **JSON Export** - Machine-readable results for CI/CD
- **SARIF Format** - Integration with security platforms

## 🚀 Use Cases

### For Development Teams
- **Pre-commit Hooks** - Block vulnerable AI code before merge
- **CI/CD Integration** - Automated security scanning in pipelines
- **Code Review** - Identify AI-generated sections needing human review
- **Technical Debt** - Track and improve code quality over time

### For Security Teams
- **Vulnerability Assessment** - Find AI-introduced security flaws
- **Risk Scoring** - Quantify codebase security posture
- **Compliance** - Meet security review requirements
- **Training** - Educate developers on AI code risks

### For Engineering Leaders
- **Productivity Metrics** - Measure real AI impact vs perception
- **Quality Gates** - Enforce code quality standards
- **Technical Strategy** - Make data-driven decisions about AI tooling
- **Team Performance** - Identify areas needing improvement

## ⚙️ Configuration

Create a `.ai-guardian.yml` file to customize analysis:

```yaml
# Security scanning settings
security:
  enabled: true
  severity_threshold: medium
  check_sql_injection: true
  check_hardcoded_secrets: true

# Performance analysis settings
performance:
  enabled: true
  max_complexity: 10
  check_memory_usage: true

# AI detection settings
ai_detection:
  enabled: true
  confidence_threshold: 0.7

# File exclusions
exclude:
  - "*.min.js"
  - "__pycache__/"
  - "node_modules/"
```

## 🔧 Advanced Usage

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Code Guardian Scan
  run: |
    pip install codeGuardian
    ai-guardian scan . --format json --output security-report.json

    # Fail build on critical issues
    if ai-guardian scan . --severity critical; then
      echo "Critical security issues found!"
      exit 1
    fi
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ai-guardian
        name: Code Guardian
        entry: ai-guardian scan
        language: system
        files: \\.py$
        args: [--severity, high]
```

### IDE Integration

```python
# VS Code settings.json
{
  "python.linting.enabled": true,
  "python.linting.ai-guardian": true,
  "ai-guardian.configFile": ".ai-guardian.yml"
}
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yes-its-shivam/codeGuardian.git
cd codeGuardian

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black . && isort . && mypy .
```
---

<div align="center">

**⭐ Star this repository if Code Guardian helps secure your codebase! ⭐**

*Built with ❤️ for developers who care about code quality and security*

[**Get Started**](https://pypi.org/project/codeGuardian/) • [**Documentation**](docs/) 

</div>
