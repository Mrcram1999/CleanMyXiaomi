"""Offline release hygiene and policy checks; does not connect to a device."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cleanmyxiaomi.policy import DATA, load_profile
from cleanmyxiaomi.storage import read_json

required = ['README.md', 'README.es.md', 'README.en.md', 'PROMPT.md', 'AGENTS.md', 'LICENSE', 'NOTICE.md', 'CONTRIBUTING.md', 'SECURITY.md']
for path in required:
    assert (ROOT / path).is_file(), f'Missing {path}'
registry = read_json(DATA / 'registry.json')
for name in registry['profiles']:
    profile = load_profile(name)
    assert profile['status'] == 'approved-audit-only', 'v0.1.0 cannot claim hardware cleanup approval'
for file in ROOT.rglob('*.md'):
    if any(p in file.parts for p in ('.git', '.venv', 'build', 'dist')):
        continue
    for link in re.findall(r'\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
        if '://' not in link and not link.startswith('#'):
            assert (file.parent / link.split('#')[0]).exists(), f'Broken link in {file}: {link}'
for workflow in (ROOT / '.github/workflows').glob('*.yml'):
    for action in re.findall(r'uses:\s*([^\s]+)', workflow.read_text()):
        assert re.fullmatch(r'[\w.-]+/[\w.-]+@[0-9a-f]{40}', action), f'Unpinned action: {action}'
print('Repository checks passed: required files, profile hashes/policy, local Markdown links, pinned actions.')
