"""Exercise a copied package, independent of checkout and working directory."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_runtime import CTX, planner, state


class PackageTests(unittest.TestCase):
    def test_copied_cli_dry_run_does_not_write_even_bytecode(self):
        source = Path(__file__).resolve().parents[1] / 'skills/github-xp'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / 'installed'
            shutil.copytree(source, package, ignore=shutil.ignore_patterns('__pycache__'))
            (root / 'context.json').write_text(json.dumps(CTX))
            (root / 'state.json').write_text(json.dumps(state()))
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = subprocess.run([sys.executable, str(package / 'scripts/xp.py'), 'velocity',
                                     '--context', str(root / 'context.json'),
                                     '--fixture', str(root / 'state.json'), '--dry-run'],
                                    cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['actions'], [])
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)

    def test_explicit_empty_scope_can_record_idle_iteration(self):
        p = planner(data={'iteration': 'i2', 'stories': [], 'availability': 'Owner unavailable; intentional empty scope'})
        p.plan()
        self.assertEqual(p.output['points'], 0)
        self.assertEqual(len(p.actions), 1)
        self.assertEqual(p.actions[0]['description'], 'Record plan')
