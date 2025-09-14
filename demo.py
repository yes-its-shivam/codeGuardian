#!/usr/bin/env python3
"""
Demo script to showcase AI Code Guardian functionality.
Run this after installing dependencies: pip install -e .
"""

import sys
from pathlib import Path

# Add src to path for demo
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def demo_ai_code_guardian():
    """Demonstrate AI Code Guardian capabilities."""

    print("🛡️ AI Code Guardian - Demo")
    print("=" * 50)

    try:
        # Import components
        from ai_code_guardian.config import Config
        from ai_code_guardian.analyzer import CodeAnalyzer

        # Initialize
        config = Config()
        analyzer = CodeAnalyzer(config)

        print("✅ Successfully initialized AI Code Guardian!")
        print(f"📊 Security Scanner: {'Enabled' if analyzer.security_scanner else 'Disabled'}")
        print(f"⚡ Performance Analyzer: {'Enabled' if analyzer.performance_analyzer else 'Disabled'}")
        print(f"🧹 Maintainability Scorer: {'Enabled' if analyzer.maintainability_scorer else 'Disabled'}")
        print(f"🤖 AI Pattern Detector: {'Enabled' if analyzer.ai_detector else 'Disabled'}")

        # Test with example files
        vulnerable_file = Path('examples/vulnerable_code.py')
        good_file = Path('examples/good_code.py')

        if vulnerable_file.exists():
            print(f"\n🔍 Scanning {vulnerable_file}...")
            results = analyzer.analyze_paths([str(vulnerable_file)])

            print(f"📋 Found {len(results.issues)} issues:")
            print(f"   🔴 Security Issues: {results.security_issues}")
            print(f"   🟡 Performance Issues: {results.performance_issues}")
            print(f"   📊 Maintainability Score: {results.maintainability_score:.1f}/10")
            print(f"   🤖 AI Generated: {results.ai_generated_percentage:.1f}%")

            # Show top 3 issues
            if results.issues:
                print("\n🚨 Top Issues:")
                for i, issue in enumerate(results.issues[:3], 1):
                    print(f"   {i}. {issue.severity.upper()}: {issue.message}")
                    print(f"      📁 {issue.file_path}:{issue.line_number}")

        print("\n🎉 Demo completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Install with: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = demo_ai_code_guardian()
    sys.exit(0 if success else 1)