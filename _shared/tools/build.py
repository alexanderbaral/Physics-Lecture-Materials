"""Joint preview first; cached full builds continue in independent queues."""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", nargs="?", default="update",
                   choices=["update","full","status","resume","ack"])
    p.add_argument("--product", choices=["script","sheets","all"], default="all")
    p.add_argument("--cloze", action="store_true", help="Include German cloze sections in the joint preview")
    args, extra = p.parse_known_args()
    if args.command == 'update' and args.product == 'all':
        if any(value != '--wait' for value in extra):
            p.error('Joint update supports --cloze and --wait. Use --product for specialist options.')
        from build_preview import update
        return update(ROOT, cloze=args.cloze, wait='--wait' in extra)
    if args.command == 'full' and '--wait' not in extra:
        extra.append('--wait')
    products = ["script","sheets"] if args.product == "all" else [args.product]
    for product in products:
        folder = "Skript" if product == "script" else "Exercise Sheets"
        options = list(extra)
        if product == 'sheets' and '--language' not in options:
            options += ['--language', 'approved']
        command = [sys.executable, "-B", str(ROOT/folder/"tools/build_coordinator.py"), args.command, *options]
        result = subprocess.run(command, cwd=ROOT/folder)
        if result.returncode:
            return result.returncode
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(str(error), file=sys.stderr, flush=True)
        sys.exit(1)

