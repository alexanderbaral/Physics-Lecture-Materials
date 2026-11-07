"""Cache directory for sheet builds and review tools."""
import importlib.util
from pathlib import Path

runtime_path = Path(__file__).resolve().parents[2] / '_shared/tools/build_runtime.py'
spec = importlib.util.spec_from_file_location('lecture_build_runtime', runtime_path)
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
CACHE_ROOT = common.cache_root('sheets')
