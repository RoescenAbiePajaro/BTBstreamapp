# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import os

# Collect MediaPipe model and asset files
mediapipe_datas = collect_data_files(
    'mediapipe',
    includes=['**/*.binarypb', '**/*.tflite', '**/*.json', '**/*.txt']
)

header_path = os.path.abspath("header")
guide_path = os.path.abspath("guide")

# Make sure icon files are properly included
icon_files = [(os.path.join('icon', f), 'icon') for f in os.listdir('icon')] if os.path.exists('icon') else []

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=mediapipe_datas + pages_files + header_files + guide_files + icon_files + static_files,
          [('VirtualPainter.py', '.'),
          ('secrets.toml', '.'),
          ('VirtualPainterEduc.py', '.'),
           ('HandTrackingModule.py', '.'),
           ('KeyboardInput.py', '.'),
           ('static/icons.png', 'static'),
           ('static/logo.png', 'static'),
           ('educators.py', '.'),
           ('student.py', '.'),
           ('register.py', '.'),
           ('pages/1_educator.py', '.'),
           ('pages/2_student.py', '.'),
           ('pages/3_register.py', '.'),
           ('icon/icons.png', 'icon'),
           ('icon/logo.png', 'icon'),
           ('header', 'header'),
           ('guide', 'guide'),
           ],  # Added icons.png explicitly

    hiddenimports=['VirtualPainter', 'HandTrackingModule', 'KeyboardInput','VirtualPainterEduc', 'student', 'register', 'pages/1_educator', 'pages/2_student', 'pages/3_register',
    'educators','pymongo', 'streamlit', 'cv2', 'numpy', 'PIL', 'tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
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
    console=False,  # set to True if you want console logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon/app.ico',  # Only specify one icon here
    sta
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BeyondTheBrush',
    icon='icon/app.ico',  # Only specify one icon here
    upx_exclude=["mediapipe", "streamlit", "pymongo", "cv2", "numpy", "PIL", "tkinter"],
)






