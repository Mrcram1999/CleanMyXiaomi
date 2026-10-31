"""Build a deterministic source ZIP from an explicit distribution allowlist."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOP = {'README.md', 'README.es.md', 'PROMPT.md', 'AGENTS.md', 'LICENSE', 'NOTICE.md', 'CONTRIBUTING.md', 'SECURITY.md', 'CHANGELOG.md', 'pyproject.toml', '.gitignore', '.gitattributes', 'MANIFEST.in'}
DIRS = {'cleanmyxiaomi', 'docs', 'scripts', 'tests', '.github'}
files = []
for p in ROOT.rglob('*'):
    rel = p.relative_to(ROOT)
    if not p.is_file() or p.is_symlink() or '__pycache__' in rel.parts or p.suffix == '.pyc':
        continue
    if len(rel.parts) == 1 and p.name in TOP or len(rel.parts) > 1 and rel.parts[0] in DIRS:
        files.append(p)
out = ROOT / 'dist'
out.mkdir(exist_ok=True)
zip_path = out / 'CleanMyXiaomi-0.1.0.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):
        info = zipfile.ZipInfo('CleanMyXiaomi/' + p.relative_to(ROOT).as_posix(), date_time=(2026, 10, 31, 0, 0, 0))
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, p.read_bytes())
checksum = hashlib.sha256(zip_path.read_bytes()).hexdigest()
(zip_path.with_suffix('.zip.sha256')).write_text(f'{checksum}  {zip_path.name}\n', encoding='ascii')
print(f'{zip_path}: {len(files)} files, sha256={checksum}')
