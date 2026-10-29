"""Validate the portable package; development-only PyYAML, not a runtime dependency."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/github-xp'
text = (SKILL / 'SKILL.md').read_text()
metadata = yaml.safe_load(text.split('---', 2)[1])
assert metadata['name'] == SKILL.name
assert isinstance(metadata['description'], str) and 0 < len(metadata['description']) <= 1024
assert len(text.splitlines()) <= 200
assert 'allowed-tools' not in metadata
for path in SKILL.rglob('*.md'):
    content = path.read_text()
    for target in re.findall(r'\]\(([^)]+)\)', content):
        if '://' in target or target.startswith('#'):
            continue
        resolved = (path.parent / target.split('#')[0]).resolve()
        assert resolved.is_relative_to(SKILL.resolve()), (path, target, 'outside package')
        assert resolved.exists(), (path, target, 'missing')
for path in (SKILL / 'assets/ISSUE_TEMPLATE').glob('*.yml'):
    form = yaml.safe_load(path.read_text())
    assert form['name'] and form['description'] and form['body']
print('Portable package metadata, links, line budget and issue forms passed.')
