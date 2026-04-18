from invoke import MockContext
from tasks import run_tests, run_lint, run_smoke, run_check

def test_test_task_logic():
    ctx = MockContext(run=True)
    run_tests(ctx)
    assert ctx.run.called
    assert "pytest" in ctx.run.call_args[0][0]

def test_lint_task_logic():
    ctx = MockContext(run=True)
    run_lint(ctx)
    assert ctx.run.called
    assert "init.sh" in ctx.run.call_args[0][0]

def test_smoke_task_logic():
    ctx = MockContext(run=True)
    run_smoke(ctx)
    assert ctx.run.called
    assert ctx.run.call_count == 4

def test_check_task_logic():
    ctx = MockContext(run=True)
    run_check(ctx)
    assert ctx.run.call_count >= 2
