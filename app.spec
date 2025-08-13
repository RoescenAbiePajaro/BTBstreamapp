# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import os
import streamlit as st
import streamlit.web.cli as stcli
import streamlit.runtime.scriptrunner
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

# Collect Streamlit package data
streamlit_path = os.path.dirname(st.__file__)
streamlit_web_path = os.path.dirname(stcli.__file__)
streamlit_runtime_path = os.path.dirname(streamlit.runtime.scriptrunner.__file__)

# Get the site-packages directory
site_packages = []
for path in sys.path:
    if 'site-packages' in path and 'Python' in path:
        site_packages.append(path)

# Find streamlit_webrtc path
streamlit_webrtc_path = None
for path in site_packages:
    webrtc_path = os.path.join(path, 'streamlit_webrtc')
    if os.path.exists(webrtc_path):
        streamlit_webrtc_path = webrtc_path
        break

# Collect Streamlit package data
streamlit_datas = [
    (streamlit_path, 'streamlit'),
    (streamlit_web_path, 'streamlit/web'),
    (streamlit_runtime_path, 'streamlit/runtime'),
]

# Add streamlit_webrtc if found
if streamlit_webrtc_path:
    streamlit_datas.append((streamlit_webrtc_path, 'streamlit_webrtc'))

# Collect your custom folders
pages_files = [(os.path.join('pages', f), 'pages') for f in os.listdir('pages')] if os.path.exists('pages') else []
header_files = [(os.path.join('header', f), 'header') for f in os.listdir('header')] if os.path.exists('header') else []
guide_files = [(os.path.join('guide', f), 'guide') for f in os.listdir('guide')] if os.path.exists('guide') else []
static_files = [(os.path.join('static', f), 'static') for f in os.listdir('static')] if os.path.exists('static') else []
icon_files = [(os.path.join('icon', f), 'icon') for f in os.listdir('icon')] if os.path.exists('icon') else []

a = Analysis(
    ['app.py'],
    pathex=[".", streamlit_path, streamlit_web_path, streamlit_runtime_path],
    binaries=[],
    datas=streamlit_datas + mediapipe_datas + pages_files + header_files + guide_files + icon_files + static_files + secret_datas + [
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
        'student', 'register','educators', 'pymongo', 'streamlit', 'cv2', 'numpy', 'PIL', 'tkinter',
        'streamlit.runtime.scriptrunner', 'streamlit.web', 'streamlit_webrtc', 'streamlit_webrtc.webrtc'
    ],
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BeyondTheBrush',
)
