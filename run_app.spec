#run_app.spec

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import os
import sys

# Get path for secrets.toml
secret_file = 'secrets.toml'
if os.path.exists(secret_file):
    secret_datas = [(secret_file, '.')]
else:
    secret_datas = []

# Collect MediaPipe model and asset files
mediapipe_datas = collect_data_files(
    'mediapipe',
    includes=['**/*.binarypb', '**/*.tflite', '**/*.json', '**/*.txt']
)

# Collect your custom folders
pages_files = [(os.path.join('pages', f), 'pages') for f in os.listdir('pages')] if os.path.exists('pages') else []
header_files = [(os.path.join('header', f), 'header') for f in os.listdir('header')] if os.path.exists('header') else []
guide_files = [(os.path.join('guide', f), 'guide') for f in os.listdir('guide')] if os.path.exists('guide') else []
static_files = [(os.path.join('static', f), 'static') for f in os.listdir('static')] if os.path.exists('static') else []
icon_files = [(os.path.join('icon', f), 'icon') for f in os.listdir('icon')] if os.path.exists('icon') else []

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas= mediapipe_datas + pages_files + header_files + guide_files + icon_files + static_files + [
        ('VirtualPainter.py', '.'),
        ('VirtualPainterEduc.py', '.'),
        ('HandTrackingModule.py', '.'),
        ('KeyboardInput.py', '.'),
        ('educators.py', '.'),
        ('student.py', '.'),
        ('register.py', '.'),
        ('pages/1_educator.py', '.'),
        ('pages/2_student.py', '.'),
        ('pages/3_register.py', '.'),
        ('header', 'header'),
        ('guide', 'guide'),
    ],
    hiddenimports=[
        'VirtualPainter', 'HandTrackingModule', 'KeyboardInput', 'VirtualPainterEduc',
        'student', 'register', 'educators', 'pymongo', 'streamlit', 'cv2', 'numpy', 'PIL', 'tkinter',
        'streamlit_webrtc', 'streamlit.components.v1', 'streamlit.runtime.scriptrunner',
        'streamlit.runtime.caching', 'pymongo.database', 'pymongo.collection', 'pymongo.mongo_client'
    ],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

for file in a.binaries:
    if 'cv2' in file[0]:
        a.binaries.append((file[0], file[1], 'BINARY'))
    if 'mediapipe' in file[0].lower():
        a.binaries.append((file[0], file[1], 'BINARY'))

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Beyond The Brush',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Beyond The Brush',
)
