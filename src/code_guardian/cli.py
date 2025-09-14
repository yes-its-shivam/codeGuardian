"""Command-line interface for Code Guardian."""

import click
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table

from .analyzer import CodeAnalyzer
from .config import Config
from .models import AnalysisResults

console = Console()


@click.group()
@click.version_option()
def cli():
    """Code Guardian - Analyze AI-generated code for quality and security issues."""
    pass


@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Configuration file path')
@click.option('--format', '-f', type=click.Choice(['json', 'html', 'cli']),
              default='cli', help='Output format')
@click.option('--output', '-o', type=click.Path(),
              help='Output file (default: stdout for CLI, auto-generated for others)')
@click.option('--severity', '-s', type=click.Choice(['low', 'medium', 'high', 'critical']),
              default='medium', help='Minimum severity level to report')
@click.option('--exclude', multiple=True, help='Patterns to exclude')
@click.option('--include-ai-patterns/--no-ai-patterns', default=True,
              help='Include AI-generated code pattern detection')
def scan(paths: tuple, config: Optional[str], format: str, output: Optional[str],
         severity: str, exclude: tuple, include_ai_patterns: bool):
    """Scan code files for quality and security issues."""

    if not paths:
        paths = ('.',)

    try:
        # Load configuration
        config_obj = Config.load(config) if config else Config()

        # Initialize analyzer
        analyzer = CodeAnalyzer(config_obj)

        # Scan files
        console.print("[bold blue]🔍 Scanning code files...[/bold blue]")

        results = analyzer.analyze_paths(
            list(paths),
            exclude_patterns=list(exclude),
            min_severity=severity,
            detect_ai_patterns=include_ai_patterns
        )

        # Generate report
        if format == 'cli':
            display_cli_report(results)
        else:
            from .report import ReportGenerator
            generator = ReportGenerator(config_obj)

            if format == 'json':
                output_file = output or 'ai-guardian-report.json'
                generator.generate_json_report(results, output_file)
            elif format == 'html':
                output_file = output or 'ai-guardian-report.html'
                generator.generate_html_report(results, output_file)

            console.print(f"[green]✅ Report saved to {output_file}[/green]")

        # Exit with error code if issues found
        if results.has_critical_issues():
            raise click.ClickException("Critical issues found!")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise click.Abort()


def display_cli_report(results):
    """Display results in CLI format."""
    console.print("\n[bold]📊 Analysis Results[/bold]\n")

    # Summary table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Status", justify="center")

    # Add summary rows
    table.add_row("Files Scanned", str(results.files_scanned), "ℹ️")
    table.add_row("Security Issues", str(results.security_issues),
                  "🔴" if results.security_issues > 0 else "✅")
    table.add_row("Performance Issues", str(results.performance_issues),
                  "🟡" if results.performance_issues > 0 else "✅")
    table.add_row("Maintainability Score", f"{results.maintainability_score:.1f}/10",
                  "🟢" if results.maintainability_score >= 7 else "🟡")
    table.add_row("AI-Generated Code", f"{results.ai_generated_percentage:.1f}%", "ℹ️")

    console.print(table)

    # Detailed issues
    if results.issues:
        console.print("\n[bold red]🚨 Issues Found:[/bold red]\n")
        for issue in results.issues[:10]:  # Show top 10
            console.print(f"[{get_severity_color(issue.severity)}]● {issue.severity.upper()}[/]: "
                         f"{issue.message} ({issue.file_path}:{issue.line_number})")

        if len(results.issues) > 10:
            console.print(f"\n... and {len(results.issues) - 10} more issues")


def get_severity_color(severity: str) -> str:
    """Get color for severity level."""
    colors = {
        'critical': 'bold red',
        'high': 'red',
        'medium': 'yellow',
        'low': 'blue'
    }
    return colors.get(severity, 'white')


@cli.command()
@click.argument('path', type=click.Path())
def init(path: str):
    """Initialize AI Guardian configuration in a directory."""
    config_path = Path(path) / '.ai-guardian.yml'

    if config_path.exists():
        console.print("[yellow]⚠️  Configuration file already exists![/yellow]")
        return

    # Create default configuration
    default_config = """# Code Guardian Configuration
version: 1

# Security scanning settings
security:
  enabled: true
  severity_threshold: medium

# Performance analysis settings
performance:
  enabled: true
  check_complexity: true
  check_memory_usage: true

# Maintainability scoring settings
maintainability:
  enabled: true
  max_complexity: 10
  max_function_length: 50

# AI pattern detection
ai_detection:
  enabled: true
  confidence_threshold: 0.7

# File patterns to exclude
exclude:
  - "*.pyc"
  - "__pycache__/"
  - ".git/"
  - "node_modules/"
  - "venv/"
  - ".env"

# Report settings
reporting:
  include_source_snippets: true
  max_issues_per_file: 20
"""

    config_path.write_text(default_config)
    console.print(f"[green]✅ Configuration initialized at {config_path}[/green]")


def main():
    """Entry point for the CLI application."""
    cli()


if __name__ == '__main__':
    main()