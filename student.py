import streamlit as st
from VirtualPainter import run_virtuals_painter

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

    st.sidebar.title("Navigation")
    
    # Add logout button at the bottom of sidebar
    st.sidebar.markdown("---")  # Add a separator
    if st.sidebar.button("Logout", key="student_portal_logout"):
        # Release camera if it exists
        if 'camera' in st.session_state:
            st.session_state.camera.release()  # Turn off camera
            del st.session_state.camera  # Clean up the session

        # Clear all session state including authentication
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Only show Virtual Painter
    st.title("Virtual Painter")
    run_virtuals_painter()

if __name__ == "__main__":
    student_portal()