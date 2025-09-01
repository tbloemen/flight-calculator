# -*- mode: python ; coding: utf-8 -*-

import os
import sys


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
    pathex=[],
    binaries=[(typst_path, "typst")],
    datas=[
        ('src/resources/airports.csv', 'src/resources'),
        ('src/templates/report.md', 'src/templates'),
        *browser_datas
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HLA-tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
