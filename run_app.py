from streamlit.web import cli
# this uri depends based on version of your streamlit

if _name_ == '_main_':
    cli._main_run_clExplicit('app.py', 'streamlit run')

# we will CREATE this function inside our streamlit framework