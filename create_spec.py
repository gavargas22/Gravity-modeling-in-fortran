#!/usr/bin/env python3
"""
Script to create PyInstaller spec file for Gravity Modeling application
"""

import os
from pathlib import Path

# Application details
APP_NAME = "gravity_modeling"
MAIN_SCRIPT = "src/gravity_modeling_app.py"
DISPLAY_NAME = "Gravity Modeling"

# Data files to include
data_files = [
    # Include models directory
    ("models", "models"),
    # Include any other data files if needed
]

# Hidden imports (dependencies that PyInstaller might miss)
hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'scipy.sparse.csgraph._validation',
    'scipy.sparse.csgraph._tools',
    'scipy._lib.messagestream',
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_qtagg',
    'pint',
    'gmm.api',
    'gmm.gm',
    'gmm.inversion_complete',
    'gmm.talw',
    'gmm.types',
]

# Analysis configuration
analysis_kwargs = {
    'pathex': ['src'],
    'binaries': [],
    'datas': data_files,
    'hiddenimports': hidden_imports,
    'hookspath': [],
    'hooksconfig': {},
    'excludes': [
        'tkinter',  # Exclude tkinter since we're using PySide6
        'matplotlib.tests',
        'numpy.tests',
        'scipy.tests',
    ],
    'win_no_prefer_redirects': False,
    'win_private_assemblies': False,
    'cipher': None,
    'noarchive': False,
}

# Executable configuration
exe_kwargs = {
    'console': True,  # Keep console for debugging, set to False for production
    'icon': None,  # Could add an icon file later
    'exclude_binaries': True,
    'name': APP_NAME,
    'debug': False,
    'bootloader_ignore_signals': False,
    'strip': False,
    'upx': True,
    'upx_exclude': [],
    'runtime_tmpdir': None,
    'compress': True,
}

# Bundle configuration (for one-folder distribution)
bundle_kwargs = {
    'name': f'{APP_NAME}_bundle',
    'version': '1.0.0',
    'description': 'Gravity and Magnetics Modeling Application',
    'author': 'Gravity Modeling Team',
    'console': True,
    'icon': None,
}

def create_spec_file():
    """Create the PyInstaller spec file"""

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(SPECPATH, 'src'))

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex={analysis_kwargs['pathex']},
    binaries={analysis_kwargs['binaries']},
    datas={analysis_kwargs['datas']},
    hiddenimports={analysis_kwargs['hiddenimports']},
    hookspath={analysis_kwargs['hookspath']},
    hooksconfig={analysis_kwargs['hooksconfig']},
    excludes={analysis_kwargs['excludes']},
    win_no_prefer_redirects={analysis_kwargs['win_no_prefer_redirects']},
    win_private_assemblies={analysis_kwargs['win_private_assemblies']},
    cipher={analysis_kwargs['cipher']},
    noarchive={analysis_kwargs['noarchive']},
)

pyz = PYZ(a.pure, a.zipped_data, cipher={analysis_kwargs['cipher']})

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_kwargs['name']}',
    debug={exe_kwargs['debug']},
    bootloader_ignore_signals={exe_kwargs['bootloader_ignore_signals']},
    strip={exe_kwargs['strip']},
    upx={exe_kwargs['upx']},
    upx_exclude={exe_kwargs['upx_exclude']},
    runtime_tmpdir={exe_kwargs['runtime_tmpdir']},
    console={exe_kwargs['console']},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={exe_kwargs['icon']},
)
'''

    with open('gravity_modeling.spec', 'w') as f:
        f.write(spec_content)

    print("✓ Created gravity_modeling.spec")
    print(f"  Main script: {MAIN_SCRIPT}")
    print(f"  Data files: {data_files}")
    print(f"  Hidden imports: {len(hidden_imports)} modules")

if __name__ == "__main__":
    create_spec_file()