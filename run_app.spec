# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata, collect_data_files
import os

# Collect MediaPipe files
mediapipe_datas = collect_data_files(
    'mediapipe',
    includes=['**/*.binarypb', '**/*.tflite', '**/*.json', '**/*.txt']
)

# Collect Streamlit files
streamlit_datas = copy_metadata('streamlit')
streamlit_data_files = collect_data_files('streamlit')

# Collect additional app folders
pages_files = [(os.path.join('pages', f), 'pages') for f in os.listdir('pages')] if os.path.exists('pages') else []
header_files = [(os.path.join('header', f), 'header') for f in os.listdir('header')] if os.path.exists('header') else []
guide_files = [(os.path.join('guide', f), 'guide') for f in os.listdir('guide')] if os.path.exists('guide') else []
static_files = [(os.path.join('static', f), 'static') for f in os.listdir('static')] if os.path.exists('static') else []
icon_files = [(os.path.join('icon', f), 'icon') for f in os.listdir('icon')] if os.path.exists('icon') else []

# --- INCLUDE .streamlit CONFIG ---
streamlit_config_files = []
if os.path.exists('.streamlit'):
    for f in os.listdir('.streamlit'):
        streamlit_config_files.append((os.path.join('.streamlit', f), '.streamlit'))

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=mediapipe_datas + streamlit_datas + streamlit_data_files +
          pages_files + header_files + guide_files + static_files + icon_files + streamlit_config_files + [
              ('app.py', '.'),
              ('VirtualPainter.py', '.'),
              ('VirtualPainterEduc.py', '.'),
              ('HandTrackingModule.py', '.'),
              ('KeyboardInput.py', '.'),
              ('educators.py', '.'),
              ('student.py', '.'),
              ('register.py', '.'),
              ('pages/1_educator.py', 'pages'),
              ('pages/2_student.py', 'pages'),
              ('pages/3_register.py', 'pages'),
              ('header', 'header'),
              ('guide', 'guide'),
              ('static', 'static'),
              ('icon', 'icon'),
          ],
    hiddenimports=[
        'VirtualPainter', 'HandTrackingModule', 'KeyboardInput', 'VirtualPainterEduc',
        'student', 'register', 'educators', 'app',
        'pymongo', 'streamlit', 'streamlit.web', 'streamlit.web.cli',
        'streamlit.runtime', 'cv2', 'numpy', 'PIL', 'altair', 'plotly', 'pandas'
    ],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BeyondTheBrush',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='BeyondTheBrush'
)
