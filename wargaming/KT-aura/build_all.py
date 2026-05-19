"""Build helper for KT aura aids.

Runs both:
1) Diagram generation
2) Single-file macro bundling
"""

import os
import subprocess
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _run_step(step_name, script_name):
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Missing required script: {script_path}")

    print(f"[{step_name}] Running {script_name}...")
    result = subprocess.run([sys.executable, script_path], cwd=SCRIPT_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"Step failed: {step_name} ({script_name})")


def main():
    _run_step("1/2", "generate_diagrams.py")
    _run_step("2/2", "build_single_macro.py")

    print("All build steps completed.")


if __name__ == "__main__":
    main()
