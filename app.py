# app.py
import streamlit as st
import time
import subprocess
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
from register import students_collection, access_codes_collection
import base64
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Beyond The Brush Portal",
    page_icon="static/icons.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ENV + DB CONNECTION ---

# --- ENV + DB CONNECTION ---
load_dotenv()

try:
    MONGODB_URI = st.secrets["MONGODB_URI"]
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI not set in secrets.toml")

    # Configure MongoDB client with updated SSL settings
    client = MongoClient(
        MONGODB_URI,
        tls=True,
        tlsAllowInvalidCertificates=False,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    # Test the connection
    client.admin.command('ping')
    db = client["beyond_the_brush"]
    students_collection = db["students"]
    access_codes_collection = db["access_codes"]
    courses_collection = db["courses"]
    blocks_collection = db["blocks"]
    year_levels_collection = db["year_levels"]
except Exception as e:
    st.error(f"MongoDB connection failed: {str(e)}")
    st.error("Please check your internet connection and MongoDB Atlas settings.")
    st.stop()

# --- SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'username' not in st.session_state:
    st.session_state.username = None

# --- STYLING ---
def load_css():
    st.markdown("""
    <style>
    body {
        background-color: #0E1117;
        color: white;
        margin: 0;
        overflow-x: hidden;
    }
                
    h1, h3 {
        text-align: center;
        color: white;
             margin: 0;
    }
    .stTextInput > div > div > input {
        background-color: rgba(30, 30, 47, 0.7) !important;
        color: white !important;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        width: 100%;
    }
    .stButton > button {
        background: #2575fc !important;
        color: white;
        border: none;
        padding: 12px 28px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(106, 17, 203, 0.3);
    }
    /* Center radio buttons */
    .stRadio > div {
        flex-direction: row;
        display: flex;
        justify-content: center;
        gap: 1rem !important;
        margin-left: 65px;
    }
    .stRadio > div > label {
        margin: 0;
    }
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        height: 10px;
        border-radius: 5px;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        margin-bottom: 100px;
        padding: 10px;
    }
    .blue-button {
        background-color: #2575fc !important;
    }
    /* Additional styling for better centering */
    .main .block-container {
        padding-top: 2rem;
    }
    /* Input field container */
    .stTextInput {
        width: 100%;
        margin-top: 0px;
    }
    /* Center the button container */
    .centered-button {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    /* Logo styling */
    .logo-container {
        text-align: center;
        margin-bottom: 10px;
    }
    .logo-img {
        height: 80px;
        margin-bottom: 5px;
    }
    .title {
        font-weight: normal;
        text-align: center;
        margin-top: 0;
        margin-bottom: 20px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- UTILS ---
def set_loading(state=True):
    st.session_state.is_loading = state

def show_loading_screen(duration=2.0):
    set_loading(True)
    with st.spinner("Launching application..."):
        time.sleep(duration)
    set_loading(False)

def launch_link(role):
    if getattr(sys, 'frozen', False):
        subprocess.Popen([sys.executable, "Link.py", role])
    else:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "Link.py", "--", role])
        time.sleep(1)
    st.markdown(f"""<meta http-equiv="refresh" content="0; url='./'">""", unsafe_allow_html=True)

# Function to encode local image to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- VERIFICATION LOGIC ---
def verify_code(code, role, name):
    try:
        # Validate access code format
        if not code.isalnum() or not all(c.isupper() or c.isdigit() for c in code):
            st.error("Access code can only contain numbers and capital letters.")
            return
            
        # Check if access code exists and is active
        code_data = access_codes_collection.find_one({"code": code, "is_active": True})
        
        if not code_data:
            st.error("Invalid or inactive access code.")
            return
        
        # Check code type matches user role
        is_admin_code = code_data.get('is_admin_code', False)
        
        if role == "student" and is_admin_code:
            st.error("Students cannot use admin access codes. Please use a student access code.")
            return
            
        if role == "educator" and not is_admin_code:
            st.error("Educators must use admin access codes. Please use an admin access code.")
            return
            
        if role == "student":
            # For students, check if they're already registered with this code
            student_data = students_collection.find_one({"access_code": code, "name": name})
            
            if student_data:
                # Student is already registered, allow login
                st.session_state.authenticated = True
                st.session_state.user_type = "student"
                st.session_state.username = name
                st.success("Access granted!")
                st.rerun()
            else:
                # Student not registered yet, redirect to registration
                st.info("Student not found. Please register first or check your name and access code.")
                st.session_state.user_type = "register"
                st.rerun()
                
        elif role == "educator":
            # For educators, just verify the access code exists and is active
            if code_data:
                st.session_state.authenticated = True
                st.session_state.user_type = "educator"
                st.success("Access granted!")
                st.rerun()
            else:
                st.error("Invalid access code.")
        else:
            st.error("Invalid role specified.")
            
    except Exception as e:
        st.error(f"Error during verification: {str(e)}")
        st.error("Please try again or contact support if the issue persists.")

# --- MAIN ---
def main():
    load_css()

    # Display the logo using base64 encoding for better reliability
    try:
        # Check if icons.png exists in the current directory
        if os.path.exists("icons.png"):
            logo_base64 = get_base64_of_bin_file("icons.png")
            st.markdown(
                f"""
                <div class="logo-container">
                    <img src="data:image/png;base64,{logo_base64}" alt="Logo" class="logo-img">
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Fallback if logo can't be found
            st.markdown(
                """
                <div class="logo-container">
                    <h1>Beyond The Brush</h1>
                </div>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        # Fallback if logo can't be loaded
        st.markdown(
            """
            <div class="logo-container">
                <h1>Beyond The Brush</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Display the title (always show this)
    st.markdown("""
    <div style="text-align: center;">
        <h1 style='font-weight: normal; margin-top: 0;'>Beyond The Brush</h1>
    </div>
""", unsafe_allow_html=True)

    if not st.session_state.authenticated:
        # Create a centered container for the login form
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])  # Adjusted column ratios for better centering
            
            with col2:  # Center column
                # Create a custom radio button layout
                st.markdown('<div class="centered-radio">', unsafe_allow_html=True)
                role = st.radio("", ["Student", "Educator"], key="role_radio", 
                               label_visibility="collapsed", horizontal=True)
                st.markdown('</div>', unsafe_allow_html=True)

                if role == "Student":
                    name = st.text_input("Enter your name:", placeholder="", key="name_input")
                    code = st.text_input("Access code:", placeholder="", type="password", key="access_code")

                    # Login button centered and full width
                    if st.button("Login", key="student_login", type="primary", use_container_width=True):
                        verify_code(code, "student", name)

                elif role == "Educator":
                    code = st.text_input("Access code:", type="password", key="admin_code")

                    # Login button centered and full width
                    if st.button("Login", key="educator_login", type="primary", use_container_width=True):
                        verify_code(code, "educator", "")

    else:
        # User is authenticated, show appropriate page
        if st.session_state.user_type == "student":
            st.switch_page("pages/2_student.py")
        elif st.session_state.user_type == "educator":
            st.switch_page("pages/1_educator.py")
        elif st.session_state.user_type == "register":
            st.switch_page("pages/3_register.py")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--painter":
        import Link
        if not st.session_state.get('access_granted'):
            st.error("Please authenticate from main screen.")
            st.stop()
        Link.run_application(sys.argv[2] if len(sys.argv) > 2 else "student")
    else:
        main()