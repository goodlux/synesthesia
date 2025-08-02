"""Build script to prepare Python code for Pyodide/WASM"""

import shutil
import json
from pathlib import Path


def create_pyodide_config():
    """Create Pyodide configuration"""
    config = {
        "packages": ["numpy"],
        "init_code": """
import sys
sys.path.append('/synesthesia')
from synesthesia.mood_analyzer import create_analyzer, analyze_text

# Create global analyzer instance
analyzer = create_analyzer()

# Export functions to JavaScript
def process_text(text):
    return analyze_text(analyzer, text)
"""
    }
    
    with open("synesthesia/static/pyodide_config.json", "w") as f:
        json.dump(config, f, indent=2)


def prepare_static_files():
    """Prepare static files for web serving"""
    static_dir = Path("synesthesia/static")
    
    # Copy Python modules
    py_dir = static_dir / "py"
    py_dir.mkdir(exist_ok=True)
    
    # Copy mood_analyzer.py
    shutil.copy("synesthesia/mood_analyzer.py", py_dir / "mood_analyzer.py")
    
    print("✓ Python modules copied to static directory")
    print("✓ Pyodide config created")
    print("\nTo run locally:")
    print("  python -m http.server 8000 --directory synesthesia/static")


if __name__ == "__main__":
    create_pyodide_config()
    prepare_static_files()