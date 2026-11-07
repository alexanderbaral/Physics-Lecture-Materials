"""Read-only source inventory; writes audit data in the external local cache."""
import os
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib
import json
import re
from pypdf import PdfReader
from cache_paths import CACHE_ROOT

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT.parent / "_shared/legacy/Exercise Sheets"
def resolve_reference(relative):
    relative = str(relative).replace(chr(92), "/")
    return LEGACY / relative[len("references/"):] if relative.startswith("references/") else ROOT / relative
def relative_name(path):
    return Path(os.path.relpath(path, ROOT)).as_posix()



def read_tex(path):
    raw = path.read_bytes()
    for encoding in ('utf-8-sig', 'cp1252'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise ValueError(f'Unknown encoding: {path}')


def uncomment(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def inventory():
    files, documents = [], []
    paths = [p for folder in (LEGACY, ROOT/'content/resources') for p in folder.rglob('*')]
    for path in sorted(paths):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        files.append(dict(path=relative_name(path), bytes=len(raw),
                          sha256=hashlib.sha256(raw).hexdigest()))
        if path.suffix != '.tex':
            continue
        text = uncomment(read_tex(path))
        text = text.split(r'\end{document}')[0]
        headings = list(re.finditer(r'\\subsection\*\{([^{}]+)\}', text))
        exercises = []
        for i, heading in enumerate(headings):
            end = headings[i+1].start() if i+1 < len(headings) else len(text)
            body = text[heading.end():end]
            dependencies = []
            for match in re.finditer(r'\\(includepdf|includegraphics|input|include)(?:\[([^\]]*)\])?\{([^{}]+)\}', body):
                kind, options, target = match.groups()
                resolved = path.parent / target
                candidates = [resolved] if resolved.suffix else [resolved.with_suffix(x) for x in ('.tex', '.pdf', '.png', '.PNG', '.jpg')]
                found = next((p for p in candidates if p.is_file()), None)
                dep = dict(kind=kind, options=options or '', target=target,
                           resolved=relative_name(found) if found else None)
                if found and found.suffix.lower() == '.pdf':
                    dep['pages'] = len(PdfReader(found).pages)
                dependencies.append(dep)
            exercises.append(dict(title=heading.group(1), line=text[:heading.start()].count('\n')+1,
                                  item_count=len(re.findall(r'\\item\b', body)), dependencies=dependencies))
        documents.append(dict(path=relative_name(path), exercises=exercises,
                              supplementary='_fremdFiles' in path.parts))
    result = dict(files=files, documents=documents)
    destination = CACHE_ROOT / 'source_inventory.json'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(files)} files, {len(documents)} LaTeX documents')
    for doc in documents:
        missing = [(e['title'], d['target']) for e in doc['exercises'] for d in e['dependencies'] if not d['resolved']]
        print(doc['path'], ':', len(doc['exercises']), 'tasks;', 'missing:', missing)
    return result


if __name__ == '__main__':
    inventory()
