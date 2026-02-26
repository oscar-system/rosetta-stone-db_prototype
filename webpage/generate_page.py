#!/usr/bin/env python3
import re
import io
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# ── Configuration ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DESCRIPTIONS_DIR = ROOT / "example_descriptions"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_FILE = ROOT / "index.html"
SYSTEMS_DIR = ROOT / "systems"

def examples_dict():
    d = {k.stem : {} for k in DESCRIPTIONS_DIR.iterdir()}
    for item in SYSTEMS_DIR.iterdir():
        for example in item.iterdir():
            data_path = None
            try:
                data_path = next(obj for obj in example.iterdir() if "data" in obj.stem)
            except StopIteration:
                print(f"Data file not found for {example.stem} and system {item.stem}")

            generate_path = None
            try:
                generate_path = next(obj for obj in example.iterdir() if "generate" in obj.stem)
            except StopIteration:
                print(f"Code file not found for {example.stem} and system {item.stem}")

            d[example.stem][item.stem] = {
                "data": data_path.read_text(),
                "generate": generate_path.read_text()
            }

    return d

if __name__ == '__main__':
    print(examples_dict())
