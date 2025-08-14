# hook-streamlit.py

from PyInstaller.utils.hooks import copy_metadata, collect_data_files, collect_submodules

# Collect Streamlit metadata
datas = copy_metadata('streamlit')

# Collect additional Streamlit data files
datas += collect_data_files('streamlit')

# Collect Altair for charts
datas += collect_data_files('altair')

# Collect Plotly for interactive plots
datas += collect_data_files('plotly')

# Collect additional Streamlit modules
hiddenimports = collect_submodules('streamlit')
hiddenimports += collect_submodules('streamlit.runtime')
hiddenimports += collect_submodules('streamlit.web')