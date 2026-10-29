"""Opt-in lifecycle checks for the published skills installer; isolated project scope only.

Requires Node/npm and network access for the pinned npm package. Does not change
real harness installations, HOME, or CODEX_HOME. Not part of unittest discovery.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = 'skills@1.7.4'
AGENTS = ['codex', 'claude-code', 'opencode', 'pi']


def files(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    checks = []
    with tempfile.TemporaryDirectory(prefix='github-xp-installer-') as temporary:
        base = Path(temporary)
        source = base / 'source'
        source_skill = source / 'skills/github-xp'
        shutil.copytree(ROOT / 'skills/github-xp', source_skill,
                        ignore=shutil.ignore_patterns('__pycache__'))
        project = base / 'project'
        project.mkdir()
        environment = dict(os.environ)
        environment.update(XDG_STATE_HOME=str(base / 'state'), XDG_CONFIG_HOME=str(base / 'config'),
                           npm_config_cache=str(base / 'npm-cache'), DISABLE_TELEMETRY='1',
                           DO_NOT_TRACK='1')

        def cli(*arguments):
            command = ['npx', '--yes', INSTALLER, *arguments]
            result = subprocess.run(command, cwd=project, env=environment,
                                    text=True, capture_output=True, timeout=120)
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            return result.stdout

        def install(copy=False):
            arguments = ['add', str(source), '--skill', 'github-xp', '-y']
            for agent in AGENTS:
                arguments.extend(['-a', agent])
            if copy:
                arguments.append('--copy')
            return cli(*arguments)

        canonical = project / '.agents/skills/github-xp'
        claude = project / '.claude/skills/github-xp'
        expected = files(source_skill)
        assert 'LICENSE' in expected and 'scripts/xp.py' in expected
        install()
        assert files(canonical) == expected
        assert claude.is_symlink() and claude.resolve() == canonical.resolve()
        checks.append('All four targets: shared canonical payload and Claude symlink; all files and license retained')
        subprocess.run(['python3', str(claude / 'scripts/xp.py'), '--help'], cwd=base,
                       check=True, capture_output=True, text=True)
        checks.append('Installed helper executes from unrelated working directory')
        install()
        assert files(canonical) == expected and files(claude) == expected
        checks.append('Identical reinstall retains one complete payload without duplicate nested directories')

        # Deliberate edits are confined to the disposable install, not source/user customizations.
        (canonical / 'LOCAL-ONLY.txt').write_text('disposable customization')
        (canonical / 'SKILL.md').write_text('disposable conflicting skill with same name')
        install()
        assert files(canonical) == expected
        checks.append('Confirmed -y reinstall replaces conflicting same-name content and removes local-only files')

        # Local sources are upgraded by reinstall, not the remote update command.
        (source_skill / 'references/installer-fixture.md').write_text('New fixture version\n')
        install()
        assert files(canonical) == files(source_skill)
        checks.append('Changed local payload propagates through reinstall to every selected target')
        unrelated = project / '.claude/skills/unrelated/SKILL.md'
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text('unrelated fixture; must survive removal')
        cli('remove', 'github-xp', '-y')
        assert not canonical.exists() and not claude.exists() and not claude.is_symlink()
        assert unrelated.exists()
        lock = project / 'skills-lock.json'
        if lock.exists():
            assert 'github-xp' not in json.loads(lock.read_text()).get('skills', {})
        checks.append('Removal cleans selected skill paths/lock entry and preserves unrelated skill')

        install(copy=True)
        assert not claude.is_symlink() and files(claude) == files(source_skill)
        assert files(canonical) == files(source_skill)
        checks.append('Copy mode supplies complete independent Claude copy plus shared universal payload')
        cli('remove', 'github-xp', '-y')
        assert not canonical.exists() and not claude.exists() and unrelated.exists()
        checks.append('Copy-mode removal preserves unrelated skill')

    result = {'installer': INSTALLER, 'scope': 'temporary project; local source',
              'targets': AGENTS, 'checks': checks,
              'not_tested': ['global harness writes', 'interactive checkbox input', 'remote changed-version update']}
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
