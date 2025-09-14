⏺ 🧪 Testing AI Code Guardian on a Separate Codebase - Step by Step

  🚀 Method 1: Test on Any Existing Project

  Step 1: Navigate to Your Target Codebase

  # Go to any Python/JavaScript project you want to test
  cd /path/to/your/project
  # Example: cd ~/projects/my-web-app

  Step 2: Activate AI Guardian Environment

  # Navigate back to AI Guardian directory
  cd /path/to/codeGuardian

  # Activate the virtual environment
  source venv/bin/activate

  Step 3: Run Basic Scan

  # Scan the external project (use absolute path)
  ai-guardian scan /path/to/your/project

  # Or navigate to the project and scan current directory
  cd /path/to/your/project
  ai-guardian scan .

  ---
  🎯 Method 2: Download and Test Popular Projects

  Step 1: Clone Popular Python Projects

  # Create a test directory
  mkdir ~/ai-guardian-tests
  cd ~/ai-guardian-tests

  # Clone some popular projects to test
  git clone https://github.com/psf/requests.git
  git clone https://github.com/pallets/flask.git
  git clone https://github.com/django/django.git
  git clone https://github.com/microsoft/vscode.git  # For JS testing

  Step 2: Test Each Project

  # Activate AI Guardian
  source /path/to/codeGuardian/venv/bin/activate

  # Test requests library
  ai-guardian scan ~/ai-guardian-tests/requests --severity high

  # Test Flask
  ai-guardian scan ~/ai-guardian-tests/flask --format html --output flask-report.html

  # Test Django (large project - use exclusions)
  ai-guardian scan ~/ai-guardian-tests/django \
    --exclude "tests/" \
    --exclude "docs/" \
    --severity critical

  ---
  🛠 Method 3: Create Test Files for Different Languages

  Step 1: Create Test Directory

  mkdir ~/test-codebase
  cd ~/test-codebase

  Step 2: Create Sample Vulnerable Files

  Python Example (vulnerable.py):
  import os
  import pickle

  # Hardcoded credentials
  API_KEY = "sk_test_1234567890abcdef"
  PASSWORD = "admin123"

  def unsafe_query(user_id):
      # SQL injection vulnerability
      query = f"SELECT * FROM users WHERE id = '{user_id}'"
      return execute_sql(query)

  def unsafe_deserialize(data):
      # Unsafe pickle usage
      return pickle.loads(data)

  def command_injection(filename):
      # Command injection
      os.system(f"cat {filename}")

  JavaScript Example (app.js):
  // Hardcoded secrets
  const API_KEY = "pk_live_1234567890abcdef";
  const secret = "mysecrettoken123";

  // XSS vulnerability
  function updateHTML(userInput) {
      document.getElementById('content').innerHTML = userInput;
  }

  // Inefficient code
  function processData(items) {
      let result = "";
      for (let i = 0; i < items.length; i++) {
          for (let j = 0; j < items[i].length; j++) {
              result += items[i][j].toString();
          }
      }
      return result;
  }

  Step 3: Test the Custom Files

  # Activate AI Guardian
  source /path/to/codeGuardian/venv/bin/activate

  # Scan your test directory
  ai-guardian scan ~/test-codebase

  ---
  📊 Method 4: Comprehensive Testing Workflow

  Step 1: Initialize Configuration

  cd /path/to/target/project
  ai-guardian init .  # Creates .ai-guardian.yml

  Step 2: Customize Configuration

  Edit the .ai-guardian.yml file:
  # Add project-specific exclusions
  exclude:
    - "node_modules/"
    - "vendor/"
    - "build/"
    - "dist/"
    - "*.min.js"
    - "test_*"
    - "*_test.py"

  # Adjust thresholds for your project
  performance:
    max_complexity: 15  # Increase for complex projects

  security:
    severity_threshold: high  # Focus on critical issues

  Step 3: Run Different Scan Types

  # Quick security-focused scan
  ai-guardian scan . --severity critical

  # Full analysis with HTML report
  ai-guardian scan . --format html --output security-report.html

  # JSON for CI/CD integration
  ai-guardian scan . --format json --output results.json

  # Focus on AI-generated code
  ai-guardian scan . --include-ai-patterns --format html --output ai-analysis.html

  Step 4: Test Different Directories

  # Scan only source code
  ai-guardian scan ./src

  # Scan multiple specific directories
  ai-guardian scan ./app ./lib ./utils

  # Scan specific file types
  ai-guardian scan ./**/*.py

  ---
  🔥 Method 5: Real-World Project Testing

  Popular Projects to Test:

  Python Projects:
  # Web frameworks
  git clone https://github.com/pallets/flask.git
  git clone https://github.com/fastapi/fastapi.git

  # Data science
  git clone https://github.com/pandas-dev/pandas.git
  git clone https://github.com/scikit-learn/scikit-learn.git

  # AI/ML projects
  git clone https://github.com/openai/openai-python.git
  git clone https://github.com/huggingface/transformers.git

  JavaScript/TypeScript Projects:
  # Frontend frameworks
  git clone https://github.com/facebook/react.git
  git clone https://github.com/vuejs/vue.git
  git clone https://github.com/angular/angular.git

  # Node.js projects
  git clone https://github.com/expressjs/express.git
  git clone https://github.com/nestjs/nest.git

  Test Commands for Each:

  # For large projects - focus on critical issues
  ai-guardian scan ./react --severity critical --exclude "node_modules/" --exclude "__tests__/"

  # For Python packages - check for common issues
  ai-guardian scan ./flask --exclude "tests/" --format html --output flask-analysis.html

  # For AI/ML projects - focus on AI patterns
  ai-guardian scan ./transformers --include-ai-patterns --severity medium

  ---
  🎯 Method 6: CI/CD Testing Setup

  Step 1: Create Test Script

  #!/bin/bash
  # test-ai-guardian.sh

  echo "🛡️ Testing AI Code Guardian on Multiple Projects"

  PROJECTS=(
      "https://github.com/psf/requests.git"
      "https://github.com/pallets/flask.git"
      "https://github.com/microsoft/TypeScript.git"
  )

  for project in "${PROJECTS[@]}"; do
      PROJECT_NAME=$(basename "$project" .git)
      echo "Testing $PROJECT_NAME..."

      git clone "$project" "test-$PROJECT_NAME" 2>/dev/null || true

      ai-guardian scan "test-$PROJECT_NAME" \
          --severity high \
          --format json \
          --output "$PROJECT_NAME-report.json"

      echo "✅ $PROJECT_NAME scan complete"
  done

  Step 2: Run Batch Tests

  chmod +x test-ai-guardian.sh
  source /path/to/codeGuardian/venv/bin/activate
  ./test-ai-guardian.sh

  ---
  📋 Quick Reference Commands

  Basic Testing

  # Simple scan
  ai-guardian scan /path/to/project

  # With severity filter
  ai-guardian scan /path/to/project --severity high

  # Generate HTML report
  ai-guardian scan /path/to/project --format html --output report.html

  Advanced Testing

  # Custom config
  ai-guardian scan /path/to/project --config custom-config.yml

  # Multiple exclusions
  ai-guardian scan /path/to/project --exclude "tests/" --exclude "docs/" --exclude "*.min.js"

  # Focus on specific categories
  ai-guardian scan /path/to/project --include-ai-patterns --severity medium

  Performance Testing

  # Time the scan
  time ai-guardian scan /path/to/large/project --severity critical

  # Memory usage monitoring
  /usr/bin/time -v ai-guardian scan /path/to/project

  ---
  🎉 Expected Results

  When testing on real codebases, you should see:

  - Security Issues: Hardcoded secrets, SQL injection, XSS vulnerabilities
  - Performance Issues: Inefficient loops, complexity problems, memory issues
  - Maintainability Issues: Long functions, poor naming, magic numbers
  - AI Patterns: Generic variable names, AI-style comments, typical AI code structures

  The tool will provide actionable insights and suggestions for each issue found!

  🚀 Pick any method above and start testing! The tool is ready to analyze any codebase.
