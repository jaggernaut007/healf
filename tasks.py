from invoke import task
import os

@task(name="test")
def run_tests(c):
    """Run all tests using pytest."""
    c.run("PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest tests/ -q", in_stream=False)

@task(name="lint")
def run_lint(c):
    """Run environment verification (init.sh logic)."""
    c.run("./scripts/init.sh", in_stream=False)

@task(name="smoke")
def run_smoke(c):
    """Run a smoke test flow checking CLI availability and help."""
    commands = [
        "python -m src.cli --help",
        "python -m src.cli enrichment --help",
        "python -m src.cli graph --help",
        "python -m src.cli orchestration --help"
    ]
    for cmd in commands:
        c.run(cmd, in_stream=False)

@task(name="check")
def run_check(c):
    """Run all quality checks: lint and test."""
    run_lint(c)
    run_tests(c)
