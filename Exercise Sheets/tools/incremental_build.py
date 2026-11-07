"""Content-based build selection; all persistent state stays in the local cache."""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import re
from pathlib import Path


def sheet_output_filename(sheet, language, solutions):
    title = sheet[3] if language == 'de' else sheet[4]
    title = title.replace('~', ' ')
    prefix = 'Übungsblatt' if language == 'de' else 'Exercise Sheet'
    stem = f"{prefix} {sheet[2]} - {title}"
    if solutions == 'on':
        stem += ' (mit Lösungen)' if language == 'de' else ' (with Solutions)'
    return stem + '.pdf'


def combined_output_filename(language, solutions):
    if solutions != 'on':
        return '_Übungsblatt Alle.pdf' if language == 'de' else '_Exercise Sheet All.pdf'
    return '_Übungsblatt Alle (mit Lösungen).pdf' if language == 'de' else '_Exercise Sheet All (with Solutions).pdf'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return {}


class Planner:
    def __init__(self, root, cache):
        self.root, self.cache = Path(root), Path(cache)
        self.stage = self.cache / 'workspace'
        self.state_path = self.cache / 'incremental_state.json'
        self.state = read_json(self.state_path)
        self.hash_path = self.cache / 'source_hashes.json'
        self.hashes = read_json(self.hash_path)

    def file_digest(self, path):
        if not path.is_file():
            return None
        stat = path.stat()
        key = str(path.resolve())
        stamp = [stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size]
        previous = self.hashes.get(key, {})
        if previous.get('stamp') != stamp:
            previous = {'stamp': stamp, 'digest': digest(path)}
            self.hashes[key] = previous
        return previous['digest']

    def save_hashes(self):
        temporary = self.hash_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.hashes), encoding='utf-8')
        temporary.replace(self.hash_path)

    def sheets(self):
        registry = (self.stage / 'common/config.tex').read_text(encoding='utf-8-sig')
        return re.findall(r'^\\DeclareSheet\{([a-z_]+)\}\{([a-z_]+)\}\{(\d+)\}\{([^{}]+)\}\{([^{}]+)\}\{([^{}]+)\}', registry, re.M)

    def fingerprint(self, language, sheet):
        sid, chapter, number, de, en, entry = sheet
        paths = {self.stage / 'main.tex', self.stage / 'latexmkrc'}
        for folder in ('common', 'tools', f'content/chapters_{language}/{chapter}',
                       f'content/resources/chapters/{chapter}', 'content/resources/shared'):
            paths.update(p for p in (self.stage / folder).rglob('*') if p.is_file())
        paths.add(self.stage / f'content/chapters_{language}/{entry}')
        # Recorder dependencies cover includes shared across chapter boundaries.
        for variant in (language, language + '_solutions'):
            runs = sorted((self.cache / f'latex_runs/{variant}/{sid}').glob('*/' + sid + '.fls'))
            if runs:
                for line in runs[-1].read_text(errors='replace').splitlines():
                    if line.startswith('INPUT '):
                        path = Path(line[6:].strip('"'))
                        if not path.is_absolute():
                            path = self.stage / path
                        path = path.resolve()
                        if path.is_relative_to(self.stage.resolve()):
                            paths.add(path)
        shared = self.stage.parent / "_shared"
        if shared.is_dir():
            entries = [p for p in shared.iterdir() if p.name.lower() not in {"legacy", "tools"}]
            paths.update(p for entry in entries for p in ([entry] if entry.is_file() else entry.rglob("*")) if p.is_file())
        values = []
        for path in sorted(paths):
            relative = ("__shared__/" + path.relative_to(shared).as_posix()
                        if shared.is_dir() and path.is_relative_to(shared)
                        else path.relative_to(self.stage).as_posix())
            values.append((relative, self.file_digest(path)))
        return hashlib.sha256(json.dumps([sheet, values], ensure_ascii=False).encode()).hexdigest()

    def plan(self):
        sheets = self.sheets()
        items = {}
        for language in ('de', 'en'):
            for sheet in sheets:
                signature = self.fingerprint(language, sheet)
                exists = (self.stage / f'content/chapters_{language}/{sheet[5]}').is_file()
                for variant in (language, language + '_solutions'):
                    key = f'{variant}/{sheet[0]}'
                    mode = 'on' if variant.endswith('_solutions') else 'off'
                    output_hash = self.file_digest(self.root / f'build/{variant}/{sheet_output_filename(sheet, language, mode)}')
                    old = self.state.get(key, {})
                    items[key] = {'signature': signature, 'reuse': bool(exists and output_hash and
                                  old.get('signature') == signature and old.get('pdf') == output_hash)}
        for variant in ('de', 'de_solutions', 'en', 'en_solutions'):
            key = variant + '/all_exercises'
            mode = 'on' if variant.endswith('_solutions') else 'off'
            output_hash = self.file_digest(self.root / f'build/{variant}/{combined_output_filename('de' if variant.startswith('de') else 'en', mode)}')
            items[key] = {'reuse': bool(output_hash and self.state.get(key, {}).get('pdf') == output_hash and
                                      all(items[f'{variant}/{s[0]}']['reuse'] for s in sheets))}
        return items

    def finish(self, results):
        if all(row.get('unchanged') and row['status'] == 'ok' for row in results):
            return
        # Re-evaluate recorder dependencies after successful builds against the fixed stage.
        items = self.plan()
        sheets = self.sheets()
        for row in results:
            variant = row['language'] + ('_solutions' if row['solutions'] == 'on' else '')
            key = variant + '/' + row['sheet']
            if row['status'] == 'ok':
                self.state[key] = {'signature': items[key].get('signature'),
                                   'pdf': self.file_digest(self.root / f'build/{variant}/{combined_output_filename(row["language"], row["solutions"])}' if row['sheet'] == 'all_exercises' else self.root / f'build/{variant}/{sheet_output_filename(next(s for s in sheets if s[0] == row["sheet"]), row["language"], row["solutions"])}')}
            else:
                self.state.pop(key, None)
        temporary = self.state_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.state, indent=2), encoding='utf-8')
        temporary.replace(self.state_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['plan', 'finish'])
    parser.add_argument('root')
    parser.add_argument('cache')
    parser.add_argument('file')
    args = parser.parse_args()
    planner = Planner(args.root, args.cache)
    if args.action == 'plan':
        Path(args.file).write_text(json.dumps(planner.plan()), encoding='utf-8')
    else:
        rows = read_json(Path(args.file))
        planner.finish(rows if isinstance(rows, list) else [rows])
    planner.save_hashes()
