# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import shutil


# Find typst binary on the system
typst_path = shutil.which("typst")
if not typst_path:
    raise RuntimeError("Could not find 'typst' binary. Make sure it's installed and in PATH.")

# Path to Playwright browsers inside venv
browsers_path = os.path.join(
    os.path.dirname(sys.executable),  # Points to .venv/Scripts
    "browsers"
)

# Make sure the folder exists (for dev-time install)
if not os.path.exists(browsers_path):
    raise RuntimeError(f"Playwright browsers not found at: {browsers_path}")

# Recursively add all files in browsers_path to datas
browser_datas = []
for root, dirs, files in os.walk(browsers_path):
    for f in files:
        src_path = os.path.join(root, f)
        rel_path = os.path.relpath(root, browsers_path)
        dest_path = os.path.join("playwright_browsers", rel_path)
        browser_datas.append((src_path, dest_path))

a = Analysis(
    ['main.py'],
    binaries=[(typst_path, "bin")],
    datas=[
        ('src/resources/airports.csv', 'src/resources'),
        ('src/templates/report.md', 'src/templates'),
        ('src/templates/report.typ', 'src/templates'),
        *browser_datas
    ],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    a.zipfiles,
    name='HLA-tool',
)
