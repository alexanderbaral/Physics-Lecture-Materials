"""Debounced source watcher. Build outputs, references and documentation are ignored."""
import sys
sys.dont_write_bytecode = True
import argparse
import subprocess
import time
from pathlib import Path


def snapshot(root):
    paths = [root / 'main.tex', root / 'latexmkrc']
    for folder in ('common', 'content', 'tools'):
        paths.extend(p for p in (root / folder).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts)
    shared = root.parent / '_shared'
    if shared.is_dir():
        entries = [p for p in shared.iterdir() if p.name.lower() not in {'legacy', 'tools'}]
        paths.extend(p for entry in entries for p in ([entry] if entry.is_file() else entry.rglob('*'))
                     if p.is_file() and not p.name.startswith('.') and p.suffix not in ('.md', '.pyc'))
    paths.extend(p for p in (root.parent / '_shared' / 'tools').glob('build*')
                 if p.is_file() and p.suffix in ('.py', '.ps1'))
    result = {}
    for path in paths:
        try:
            stat = path.stat()
            result[str(path)] = (stat.st_mtime_ns, stat.st_size)
        except FileNotFoundError:
            pass
    return result


def watch(root, command, once=False, settle=1.0):
    previous = None
    while True:
        current = snapshot(root)
        if current == previous:
            time.sleep(0.5)
            continue
        # Wait until an editor's sequence of writes/renames has settled.
        while True:
            time.sleep(settle)
            latest = snapshot(root)
            if current == latest:
                break
            current = latest
        previous = current  # Changes during the build remain pending for the next loop.
        print('Updating exercise sheets...', flush=True)
        status = subprocess.run(command, cwd=root).returncode
        print('Sheet outputs ready; collection PDFs may continue in the background.' if status == 0 else
              'Build failed. See errors above; the next save will retry.', flush=True)
        if once:
            return status
        print('Watching sources. Stop with Ctrl+C.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', choices=['de', 'en', 'all'], default='de')
    parser.add_argument('--solutions', choices=['both', 'on', 'off'], default='both')
    parser.add_argument('--jobs', type=int, choices=range(1, 17), default=4)
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
               str(root / 'tools/build-all.ps1'), '-Language', args.language,
               '-Solutions', args.solutions, '-Jobs', str(args.jobs), '-Incremental',
               '-Python', sys.executable]
    try:
        sys.exit(watch(root, command, args.once))
    except KeyboardInterrupt:
        print('\nDevelopment watcher stopped.', flush=True)
        sys.exit(130)
