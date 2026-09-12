"""Bounded publication checks; not a comprehensive secret or privacy scanner."""
from pathlib import Path
import contextlib
import io
import json
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from atlas import export_demo

manifest = json.loads((ROOT / 'public-manifest.json').read_text())
allowed = set(manifest['files'])
actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()
          and not any(part in {'.git', 'work', '__pycache__'} for part in p.relative_to(ROOT).parts)}
assert actual == allowed, f'File manifest mismatch: extra={actual-allowed}, missing={allowed-actual}'
patterns = [r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{30,}',
            r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
            r'/subscriptions/[0-9a-fA-F-]{36}', r'https://[^\s]+\.azuredatabricks\.net',
            r'[A-Za-z]:\\Users\\[^\s]+', r'(?i)AccountKey=[A-Za-z0-9+/=]{20,}']
for relative in sorted(allowed):
    p = ROOT / relative
    assert p.suffix.lower() in {'.md', '.py', '.sql', '.json', '.csv', '.svg', '.pq', '.dax', '.yml', ''}, relative
    content = p.read_text(encoding='utf-8')
    assert '\x00' not in content, 'Binary content: ' + relative
    for pattern in patterns:
        assert not re.search(pattern, content), 'Possible sensitive pattern: ' + relative
    if p.suffix == '.md':
        for target in re.findall(r'\]\(([^)]+)\)', content):
            if target.startswith(('https://', 'http://', '#')):
                continue
            link = (p.parent / target.split('#')[0]).resolve()
            assert link.is_relative_to(ROOT) and link.exists(), f'Broken/escaping link: {relative}: {target}'
with tempfile.TemporaryDirectory() as temp:
    destination = Path(temp)
    with contextlib.redirect_stdout(io.StringIO()):
        export_demo(destination)
    for output in destination.iterdir():
        assert output.read_bytes() == (ROOT / 'examples' / output.name).read_bytes(), 'Export drift: ' + output.name
print(f'PASS: {len(allowed)} allowlisted text files; relative links, bounded pattern scan and regenerated exports')
