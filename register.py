# register.py
import streamlit as st
from pymongo import MongoClient
import time
import subprocess
import os
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection with error handling
try:
    # Try to get MongoDB URI from secrets first
    try:
        MONGODB_URI = st.secrets["MONGODB_URI"]
    except:
        # Fallback to environment variable for PyInstaller compatibility
        MONGODB_URI = os.getenv("MONGODB_URI")
    
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI not set in secrets.toml or environment variables")
    
    # Configure MongoDB client with SSL settings
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
    access_codes_collection = db["access_codes"]
    students_collection = db["students"]
except Exception as e:
    st.error(f"MongoDB connection failed: {str(e)}")
    st.error("Please check your internet connection and MongoDB Atlas settings.")
    st.stop()


def register_student():
    st.markdown("""
    <style>
    .stTextInput > div > div > input {
        color: white !important;
        background-color: rgba(30, 30, 47, 0.7) !important;
        padding: 12px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
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
    .back-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }
    .back-btn button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(106, 17, 203, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Student Registration")

    with st.form("registration_form"):
        name = st.text_input("Username", placeholder="Enter your Username")
        access_code = st.text_input("Access Code", placeholder="Ask your educator for the access code")

        submitted = st.form_submit_button("Register")

        if submitted:
            if not name or not access_code:
                st.error("Please fill in all fields")
            elif len(name) != 8:
                st.error("Name must be exactly 8 characters long")
            else:
                # Check if name already exists
                existing_student = students_collection.find_one({"name": name})
                if existing_student:
                    st.warning("This name is already registered. Please use a different name.")
                else:
                    # Check if access code exists and is active in MongoDB
                    code_data = access_codes_collection.find_one({"code": access_code.strip().upper(), "is_active": True})
                    if code_data:
                        # Check if max uses limit is reached
                        current_uses = students_collection.count_documents({"access_code": access_code.strip().upper()})
                        max_uses = code_data.get("max_uses")
                        
                        if max_uses and current_uses >= max_uses:
                            st.error(f"Access code '{access_code}' has reached its maximum usage limit ({max_uses} students).")
                            st.info("Please ask your educator for a new access code.")
                        else:
                            # Register student
                            student_data = {
                                "name": name,
                                "access_code": access_code.strip().upper(),
                                "registered_at": time.time(),
                                "educator_id": code_data.get("educator_id", "Admin"),
                                "registration_date": time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            students_collection.insert_one(student_data)
                            st.success("Registration successful! You can now log in.")
                            st.info(f"Welcome, {name}! Use your name and access code '{access_code}' to log in.")
                    else:
                        st.error("Invalid or inactive access code. Please ask your educator for a valid code.")
                        st.info("Make sure the code is spelled correctly and hasn't expired.")

    # Add Back button
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    col1, col2, col3 = st.columns([1,2,1])  # Create 3 columns with middle one being wider
    with col2:  # Place button in middle column
        if st.button("← Back to Login", use_container_width=True):
            st.markdown("<meta http-equiv='refresh' content='0; url=./' />", unsafe_allow_html=True)

if __name__ == "__main__":
    register_student()