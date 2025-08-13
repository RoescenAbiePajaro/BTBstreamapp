from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all Streamlit data files
datas = collect_data_files('streamlit')

# Collect all Streamlit submodules
hiddenimports = collect_submodules('streamlit')

# Add any additional Streamlit components that might be needed
hiddenimports.extend([
    'streamlit_webrtc',
    'streamlit.components.v1',
    'streamlit.runtime.scriptrunner',
    'streamlit.runtime.caching',
])