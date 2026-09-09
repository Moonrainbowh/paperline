"""Local Paperline workbench. Run: python -X utf8 webui/server.py."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import subprocess
import sys
import threading
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).parent / 'static'
SKILLS = ['paperline', 'paper-navigator', 'journal-navigator', 'zh-en-paper-translator']
CHECKS = {
    'contracts': ('跨 Skill 合同演练', 'paperline/scripts/run_contract_dry_run.py', []),
    'state': ('流水线状态与失效规则', 'paperline/scripts/validate_pipeline_state.py', ['--self-test']),
    'journal': ('期刊决策与写作契约', 'journal-navigator/scripts/validate_journal_artifacts.py', ['--self-test']),
    'handoff': ('翻译交接门', 'zh-en-paper-translator/scripts/validate_pipeline_handoff.py', ['--self-test']),
    'translation': ('译文完整性审计', 'zh-en-paper-translator/scripts/audit_translation.py', ['--self-test']),
    'structure': ('文档结构审计', 'zh-en-paper-translator/scripts/audit_document_structure.py', ['--self-test']),
    'references': ('参考文献与术语资源', 'zh-en-paper-translator/scripts/validate_reference_data.py', []),
}
LOCK = threading.Lock()
RESULTS = {}


def files():
    return sorted(p.relative_to(ROOT).as_posix() for skill in SKILLS
                  for p in (ROOT / skill).rglob('*')
                  if p.is_file() and p.suffix in {'.md', '.py', '.yaml', '.tsv'} and '__pycache__' not in p.parts)


def snapshot():
    inventory = files()
    runs = []
    for p in sorted((ROOT / 'runs').glob('*/records.json')):
        try:
            records = json.loads(p.read_text(encoding='utf-8-sig'))
            runs.append({'name': p.parent.name, 'records': records, 'path': p.relative_to(ROOT).as_posix()})
        except (ValueError, OSError) as exc:
            runs.append({'name': p.parent.name, 'error': str(exc)})
    with LOCK:
        checks = [dict(id=k, title=v[0], path=v[1], **RESULTS.get(k, {'status': 'idle'})) for k, v in CHECKS.items()]
    return {'files': inventory, 'skills': SKILLS, 'checks': checks, 'runs': runs,
            'states': [p.relative_to(ROOT).as_posix() for p in (ROOT / 'runs').rglob('pipeline-state.json')],
            'scanned_at': datetime.now(timezone.utc).isoformat()}


def run_check(key):
    _, path, args = CHECKS[key]
    try:
        result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / path), *args],
                                cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        record = {'status': 'passed' if result.returncode == 0 else 'failed',
                  'output': (result.stdout + result.stderr)[-60000:], 'exit_code': result.returncode}
    except Exception as exc:
        record = {'status': 'failed', 'output': str(exc)}
    record['finished_at'] = datetime.now(timezone.utc).isoformat()
    with LOCK:
        RESULTS[key] = record


class Handler(BaseHTTPRequestHandler):
    def send(self, data, status=200, mime='application/json; charset=utf-8'):
        body = json.dumps(data, ensure_ascii=False).encode() if mime.startswith('application/json') else data
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path)
        if route.path == '/api/overview':
            return self.send(snapshot())
        if route.path == '/api/file':
            name = parse_qs(route.query).get('path', [''])[0]
            allowed = files() + [p.relative_to(ROOT).as_posix() for p in (ROOT / 'runs').glob('*/records.json')]
            if name not in allowed or not (ROOT / name).resolve().is_relative_to(ROOT):
                return self.send({'error': '文件不在可读清单中'}, 404)
            return self.send({'path': name, 'content': (ROOT / name).read_text(encoding='utf-8-sig')})
        name = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css'}.get(route.path)
        if not name:
            return self.send({'error': 'Not found'}, 404)
        mime = {'html': 'text/html', 'js': 'text/javascript', 'css': 'text/css'}[name.split('.')[-1]]
        self.send((STATIC / name).read_bytes(), mime=mime + '; charset=utf-8')

    def do_POST(self):
        # Only the same-origin local UI may launch an allowlisted check.
        origin = self.headers.get('Origin')
        if origin and origin != f'http://{self.headers.get("Host")}':
            return self.send({'error': 'Origin rejected'}, 403)
        if self.headers.get('X-Paperline') != 'workbench':
            return self.send({'error': 'Missing workbench header'}, 403)
        key = self.path.removeprefix('/api/checks/')
        if self.path != '/api/checks/' + key or key not in CHECKS:
            return self.send({'error': 'Unknown check'}, 404)
        with LOCK:
            if any(v['status'] == 'running' for v in RESULTS.values()):
                return self.send({'error': '已有校验正在运行'}, 409)
            RESULTS[key] = {'status': 'running'}
        threading.Thread(target=run_check, args=(key,), daemon=True).start()
        self.send({'status': 'running'}, 202)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    print(f'Paperline: http://127.0.0.1:{args.port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
