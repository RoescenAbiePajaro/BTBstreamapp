# student.py
import streamlit as st

# Add loading screen CSS
st.markdown(
    """
    <style>
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        height: 10px;
        border-radius: 5px;
    }

    body {
        background-color: #0E1117;
        color: white;
        
    }

    
    /* Card-like containers */
    .container {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 38px;
        padding: 0 16px;
        
    }
    
    /* Form fields */
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    
    /* Metrics */
    .css-1r6slb0 {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
    }
    
    /* Headers */
    h1, h2, h3 {
        margin-bottom: 1rem;
    }
    
    /* Columns spacing */
    .row-widget.stRadio > div {
        display: flex;
        justify-content: space-between;
    }
    
    /* Navigation sidebar */
    .css-1d391kg {
        padding: 1rem;
    }
    
    /* Status indicators */
    .status-active {
        color: #09ab3b;
        font-weight: bold;
    }
    .status-inactive {
        color: #ff4b4b;
        font-weight: bold;
    }

    .st-emotion-cache-zy6yx3 {
    width: 100%;
    padding: 2rem 1rem 10rem;
    max-width: initial;
    min-width: auto;
}
    </style>
    """,
    unsafe_allow_html=True,
)

# Import Link with error handling for PyInstaller compatibility
try:
    from Link import run_link
except ImportError as e:
    st.error(f"Failed to import Link: {e}")
    def run_link():
        st.error("Link module not available in this build.")
        st.info("Please ensure all dependencies are properly included.")

st.set_page_config(layout="wide")

def clear_session_state():
    """Clear all session state variables and release resources"""
    # Don't clear authentication state
    auth_state = st.session_state.get('authenticated')
    user_type = st.session_state.get('user_type')

    # Clear all other session state variables except authentication
    for key in list(st.session_state.keys()):
        if key not in ['authenticated', 'user_type']:
            del st.session_state[key]

    # Restore authentication state
    if auth_state:
        st.session_state.authenticated = auth_state
    if user_type:
        st.session_state.user_type = user_type

def student_portal():
    """Main entry point for the student portal"""
    # Check authentication state
    if not st.session_state.get('authenticated') or st.session_state.get('user_type') != 'student':
        st.error("Access denied. Please login as a student.")
        st.stop()

    if st.sidebar.button("Logout", key="student_portal_logout"):
        # Release camera if it exists (handle both 'camera' and 'cap' keys)
        for camera_key in ['camera', 'cap']:
            if camera_key in st.session_state:
                try:
                    if hasattr(st.session_state[camera_key], 'release'):
                        st.session_state[camera_key].release()
                except Exception:
                    pass
                finally:
                    del st.session_state[camera_key]

        # Clear all session state including authentication
        for key in list(st.session_state.keys()):
            try:
                del st.session_state[key]
            except Exception:
                pass
        st.rerun()

    # Only show Virtual Painter
    st.title("")
    run_link()

if __name__ == "__main__":
    student_portal()