  📚 Complete Usage Guide

  🛡️ Code Guardian - Complete Usage Guide

  🚀 Installation

  Method 1: Quick Install

  git clone https://github.com/yes-its-shivam/codeGuardian.git
  cd codeGuardian
  ./install.sh
  source venv/bin/activate

  Method 2: Manual Install

  git clone https://github.com/yes-its-shivam/codeGuardian.git
  cd codeGuardian
  python3 -m venv venv
  source venv/bin/activate
  pip install -e .

  🎯 Basic Commands

  1. Get Help

  ai-guardian --help
  ai-guardian scan --help

  2. Initialize Configuration

  ai-guardian init .                    # Initialize in current directory
  ai-guardian init /path/to/project     # Initialize in specific directory

  3. Basic Scanning

  ai-guardian scan .                    # Scan current directory
  ai-guardian scan src/                 # Scan specific directory
  ai-guardian scan file.py             # Scan specific file
  ai-guardian scan *.py                 # Scan Python files

  ⚙️ Advanced Usage

  4. Severity Filtering

  ai-guardian scan . --severity critical    # Only show critical issues
  ai-guardian scan . --severity high        # Show high+ severity issues
  ai-guardian scan . --severity medium      # Show medium+ severity (default)
  ai-guardian scan . --severity low         # Show all issues

  5. Output Formats

  # CLI Output (default)
  ai-guardian scan .

  # HTML Report
  ai-guardian scan . --format html --output report.html

  # JSON Report
  ai-guardian scan . --format json --output report.json

  6. Configuration Options

  ai-guardian scan . --config .ai-guardian.yml     # Use custom config
  ai-guardian scan . --exclude "*.min.js"          # Exclude patterns
  ai-guardian scan . --exclude "node_modules/"     # Exclude directories
  ai-guardian scan . --no-ai-patterns              # Skip AI detection

  7. Multiple Exclusions

  ai-guardian scan . \
    --exclude "*.pyc" \
    --exclude "__pycache__/" \
    --exclude "venv/" \
    --exclude "node_modules/"

  📊 Report Examples

  HTML Report Features

  - Interactive Dashboard with metrics
  - Color-coded Issues by severity
  - File-by-file Breakdown
  - AI Pattern Analysis
  - Actionable Suggestions

  JSON Report Structure

  {
    "metadata": {
      "tool": "Code Guardian",
      "version": "0.1.0",
      "generated_at": "2024-01-15T10:30:00",
      "execution_time": 2.43
    },
    "summary": {
      "files_scanned": 42,
      "security_issues": 7,
      "performance_issues": 12,
      "maintainability_score": 6.8,
      "ai_generated_percentage": 73.2
    },
    "issues": [...],
    "file_scores": {...}
  }

  ⚙️ Configuration File

  Sample .ai-guardian.yml

  # Security Settings
  security:
    enabled: true
    severity_threshold: medium
    check_sql_injection: true
    check_hardcoded_secrets: true
    check_unsafe_deserialization: true

  # Performance Settings
  performance:
    enabled: true
    max_complexity: 10
    check_memory_usage: true
    check_inefficient_loops: true

  # Maintainability Settings
  maintainability:
    enabled: true
    max_function_length: 50
    max_class_methods: 20
    check_naming_conventions: true

  # AI Detection Settings
  ai_detection:
    enabled: true
    confidence_threshold: 0.7
    check_comment_patterns: true
    check_code_patterns: true

  # Exclusion Patterns
  exclude:
    - "*.pyc"
    - "__pycache__/"
    - ".git/"
    - "node_modules/"
    - "venv/"
    - "*.min.js"
    - "*.min.css"

  # Report Settings
  reporting:
    include_source_snippets: true
    max_issues_per_file: 20
    show_ai_confidence: true

  🔧 CI/CD Integration

  GitHub Actions

  name: AI Code Security Scan
  on: [push, pull_request]

  jobs:
    security-scan:
      runs-on: ubuntu-latest
      steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9+'

      - name: Install Code Guardian
        run: |
          pip install codeGuardian

      - name: Run Security Scan
        run: |
          ai-guardian scan . --format json --output security-report.json
          ai-guardian scan . --severity critical  # Fail on critical issues

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security-report.json

  Pre-commit Hook

  # .pre-commit-config.yaml
  repos:
    - repo: local
      hooks:
        - id: ai-guardian
          name: Code Guardian Security Scan
          entry: ai-guardian scan
          language: system
          files: \\.py$
          args: [--severity, high]

  🎯 Real-World Examples

  Example 1: Enterprise Security Review

  # Comprehensive scan for security review
  ai-guardian scan . \
    --format html \
    --output security-audit-$(date +%Y%m%d).html \
    --severity medium \
    --config enterprise-config.yml

  Example 2: CI Pipeline Integration

  # Quick scan for CI pipeline
  ai-guardian scan src/ \
    --severity critical \
    --format json \
    --output ci-security-report.json \
    --exclude "tests/" \
    --exclude "docs/"

  Example 3: AI Code Review

  # Focus on AI-generated code patterns
  ai-guardian scan . \
    --include-ai-patterns \
    --format html \
    --output ai-review-report.html

  📈 Performance Tips

  1. Use Exclusions: Exclude unnecessary files (tests, docs, vendor code)
  2. Severity Filtering: Use higher severity levels for faster scans
  3. Specific Paths: Scan only changed files in large codebases
  4. Configuration: Disable unused analyzers in config

  🐛 Troubleshooting

  Common Issues

  ImportError on startup
  # Ensure you're in the virtual environment
  source venv/bin/activate
  pip install -e .

  "Critical issues found" error
  # This is intentional - the tool exits with error code on critical issues
  # Use different severity level to avoid this:
  ai-guardian scan . --severity high

  No issues found in obviously problematic code
  # Check if the right analyzers are enabled
  ai-guardian scan . --config .ai-guardian.yml
  # Or create a new config
  ai-guardian init .

  Debug Mode

  # Enable verbose output (future feature)
  ai-guardian scan . --verbose

  🎓 Understanding Results

  Severity Levels

  - 🔴 CRITICAL: Security vulnerabilities, major risks
  - 🟠 HIGH: Performance issues, security concerns
  - 🟡 MEDIUM: Code quality, maintainability issues
  - 🔵 LOW: Style issues, minor improvements

  AI Detection Confidence

  - 90-100%: Very likely AI-generated
  - 70-89%: Probably AI-generated
  - 50-69%: Possibly AI-generated
  - <50%: Likely human-written

  Maintainability Score

  - 8-10: Excellent code quality
  - 6-7: Good code quality
  - 4-5: Needs improvement
  - 0-3: Poor code quality
