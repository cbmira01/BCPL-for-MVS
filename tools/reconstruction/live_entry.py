"""Guarded public entry point for the single-TK5 reconstruction controller.

This module performs no work on import. The existing run.authorized_run owns the
scoped approval, exclusive submission window, JES preflight and build engine.
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
import sys
import types
from typing import Callable


def load_extensionless(path: Path, name: str):
    """Load the existing extensionless project tool without running its CLI."""
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    if spec is None:
        raise RuntimeError(f'cannot import project tool: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def observe_jes(root: Path, emit: Callable[[str], None]):
    """Return exactly the check_twice() result, with user-visible evidence."""
    probe = load_extensionless(root / 'tools/reconstruction/jes-idle',
                               'reconstruction_live_jes_idle')
    console = probe.load_mvs_console(root / 'tools/mvs/mvs-console')
    def capture(command):
        return console.capture(command, timeout=10.0, settle=2.0)
    ok, observations = probe.check_twice(capture)
    for number, obs in enumerate(observations, 1):
        emit(f'JES2 $DA {number}/2: {obs.state} — {obs.reason}')
        for line in obs.evidence:
            emit('  ' + line)
    return ok, observations


def run_live(root: Path, authorized_run, execute_project_command, *,
             stdin=None, stdout=None, emit=None, prompt=None,
             observe=observe_jes) -> int:
    """Require a real terminal; do not turn failures into apparent success.

    Only a separately operator-acknowledged plan may call the stage runner.
    There is deliberately no --yes or reusable authorization token.
    """
    stdin = sys.stdin if stdin is None else stdin
    stdout = sys.stdout if stdout is None else stdout
    emit = (lambda msg: print(msg, flush=True)) if emit is None else emit
    prompt = input if prompt is None else prompt
    if not (stdin.isatty() and stdout.isatty()):
        emit('BLOCKED: reconstruction requires interactive input and output terminals.')
        return 2
    try:
        plan = load_extensionless(root / 'tools/reconstruction/plan',
                                  'reconstruction_live_plan')
        approval = load_extensionless(root / 'tools/reconstruction/authorize',
                                      'reconstruction_live_authorize')
        core = plan.load_dspal_core(root)
        emit('One-TK5 clean-room reconstruction: review all managed dataset deletions.')
        emit('Dedicated TK5: do not submit independent jobs during reconstruction.')
        emit('JES2 idle checks do not reserve or lock the system.')
        authorized_run(root, plan, approval, core,
                       lambda command: execute_project_command(root, command),
                       emit, prompt=prompt, terminal=True,
                       jes_idle_guard=lambda: observe(root, emit))
        emit('RECONSTRUCTION OPERATIONS COMPLETED; see the durable attempt report.')
        return 0
    except (KeyboardInterrupt, EOFError):
        emit('INTERRUPTED: reconstruction cancelled or operator input closed.')
        return 130
    except Exception as exc:
        # Never surface exception text on the operator console: downstream
        # tools may accidentally include MVS credentials in error messages.
        # Detailed operation diagnostics belong in the redacted evidence log.
        emit(f'BLOCKED/FAILED: {type(exc).__name__}; consult preserved evidence if available.')
        return 2
