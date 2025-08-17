# educators.py
import streamlit as st
import subprocess
import time
from pymongo import MongoClient
from contextlib import contextmanager

# Import Links with error handling for PyInstaller compatibility
try:
    from Linkeduc import run_link_educator
except ImportError as e:
    st.error(f"Failed to import Linkeduc: {e}")
    def run_link_educator():
        st.error("Link Educator module not available in this build.")
        st.info("Please ensure all dependencies are properly included.")


st.set_page_config(
    page_title="Educator Portal",
    page_icon="static/icons.png",
    layout="wide"
)

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
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for Virtual Painter if not exists
if 'link_educator_active' not in st.session_state:
    st.session_state.link_educator_active = False


@contextmanager
def get_mongodb_connection():
    """Context manager for MongoDB connection"""
    client = None
    try:
        # Try to get MongoDB URI from secrets first
        try:
            MONGODB_URI = st.secrets["MONGODB_URI"]
        except:
            # Fallback to environment variable for PyInstaller compatibility
            import os
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
        students_collection = db["students"]
        access_codes_collection = db["access_codes"]
        yield students_collection, access_codes_collection
    except Exception as e:
        st.error(f"MongoDB connection failed: {str(e)}")
        st.error("Please check your internet connection and MongoDB Atlas settings.")
        st.stop()
    finally:
        if client:
            client.close()


def clear_session_state():
    """Clear all session state variables and release resources"""
    # Don't clear authentication state
    auth_state = st.session_state.get('authenticated')
    user_type = st.session_state.get('user_type')

    # Release camera if it exists (handle both 'cap' and 'camera' keys)
    for camera_key in ['cap', 'camera']:
        if camera_key in st.session_state:
            try:
                if hasattr(st.session_state[camera_key], 'release'):
                    st.session_state[camera_key].release()
            except Exception:
                pass  # Ignore errors during cleanup
            finally:
                del st.session_state[camera_key]

    # Clear virtual painter state
    if 'link_educator_active' in st.session_state:
        del st.session_state.link_educator_active

    # Clear camera initialization state
    if 'camera_initialized' in st.session_state:
        del st.session_state.camera_initialized

    # Clear editing state
    if 'editing_student' in st.session_state:
        del st.session_state.editing_student

    # Clear all other session state variables except authentication
    for key in list(st.session_state.keys()):
        if key not in ['authenticated', 'user_type']:
            try:
                del st.session_state[key]
            except Exception:
                pass  # Ignore errors during cleanup

    # Restore authentication state
    if auth_state:
        st.session_state.authenticated = auth_state
    if user_type:
        st.session_state.user_type = user_type


def admin_portal():
    # Check authentication state
    if not st.session_state.get('authenticated') or st.session_state.get('user_type') != 'educator':
        st.error("Access denied. Please login as an educator.")
        st.stop()

    # Initialize session state for navigation if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Student Registrations"

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Student Registrations", "Access Codes", "Beyond The Brush App"])

    # Update current page in session state
    st.session_state.current_page = page

    # Debug information
    st.sidebar.write(f"Current page: {page}")

    # Add logout button at the bottom of sidebar
    st.sidebar.markdown("---")  # Add a separator
    if st.sidebar.button("Logout", key="educator_portal_logout"):
        # Release camera if it exists
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

        # Redirect to main page
        st.markdown(
            """
            <meta http-equiv="refresh" content="0; url=./" />
            """,
            unsafe_allow_html=True
        )
        st.stop()

    # Clear virtual painter state when switching to other pages
    if page != "Beyond The Brush App" and st.session_state.get('link_educator_active'):
        clear_session_state()
        st.session_state.link_educator_active = False
        st.rerun()

    if page == "Student Registrations":
        st.session_state.link_educator_active = False
        st.title("Student Registrations")

        with get_mongodb_connection() as (students_collection, _):
            # Display all registered students
            students = list(students_collection.find())

            if students:
                for student in students:
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        st.write(f"**{student['name']}** (Registered: {time.ctime(student['registered_at'])})")
                    with col2:
                        if st.button(f"Edit {student['name']}", key=f"edit_{student['_id']}"):
                            st.session_state['editing_student'] = student['_id']
                    with col3:
                        if st.button(f"Delete {student['name']}", key=f"delete_{student['_id']}"):
                            students_collection.delete_one({"_id": student["_id"]})
                            st.rerun()

                # Show edit form if a student is being edited
                if 'editing_student' in st.session_state:
                    student_to_edit = next((s for s in students if s['_id'] == st.session_state['editing_student']),
                                           None)
                    if student_to_edit:
                        with st.form(key=f"edit_form_{student_to_edit['_id']}"):
                            new_name = st.text_input("New Name", value=student_to_edit['name'])
                            submit_edit = st.form_submit_button("Save Changes")
                            cancel_edit = st.form_submit_button("Cancel")

                            if submit_edit and new_name:
                                students_collection.update_one(
                                    {"_id": student_to_edit["_id"]},
                                    {"$set": {"name": new_name}}
                                )
                                del st.session_state['editing_student']
                                st.success("Student information updated successfully!")
                                st.rerun()

                            if cancel_edit:
                                del st.session_state['editing_student']
                                st.rerun()
            else:
                st.info("No students registered yet.")

    elif page == "Access Codes":
        st.session_state.link_educator_active = False
        st.title("Access Codes Management")
        


        try:
            with get_mongodb_connection() as (students_collection, access_codes_collection):
                # Display existing access codes
                codes = list(access_codes_collection.find())
                
                # Get student count for each code
                student_counts = {}
                try:
                    for code in codes:
                        # Only count students for active access codes
                        if code.get('is_active', True):
                            count = students_collection.count_documents({"access_code": code["code"]})
                            student_counts[code["code"]] = count
                        else:
                            student_counts[code["code"]] = 0
                except Exception as e:
                    st.warning(f"Could not retrieve student counts: {str(e)}")
                    # Set default counts to 0
                    student_counts = {code["code"]: 0 for code in codes}

                if codes:
                    st.subheader("Available Access Codes")
                    for code in codes:
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                        with col1:
                            st.code(code['code'], language=None)
                            # Show active status
                            status_color = "🟢" if code.get('is_active', True) else "🔴"
                            status_text = "Active" if code.get('is_active', True) else "Inactive"
                            st.write(f"{status_color} {status_text}")
                        with col2:
                            created_time = time.ctime(code.get('created_at', 0))
                            st.write(f"Created: {created_time}")
                            st.write(f"By: {code.get('educator_id', 'System')}")
                        with col3:
                            student_count = student_counts.get(code['code'], 0)
                            st.metric("Students Used", student_count)
                        with col4:
                            # Toggle active status
                            toggle_key = f"toggle_{code['_id']}"
                            current_status = code.get('is_active', True)
                            new_status = not current_status
                            
                            if st.button(
                                "🔄 Toggle" if current_status else "✅ Activate", 
                                key=toggle_key,
                                help=f"{'Deactivate' if current_status else 'Activate'} access code {code['code']}"
                            ):
                                try:
                                    access_codes_collection.update_one(
                                        {"_id": code["_id"]},
                                        {"$set": {"is_active": new_status}}
                                    )
                                    st.success(f"Access code '{code['code']}' {'deactivated' if not new_status else 'activated'} successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to update access code status: {str(e)}")
                        with col5:
                            # Use a unique key for the delete button
                            delete_btn_key = f"delete_btn_{code['_id']}"
                            
                            if st.button(f"🗑️ Delete", key=delete_btn_key, help=f"Delete access code {code['code']}"):
                                try:
                                    access_codes_collection.delete_one({"_id": code["_id"]})
                                    st.success(f"Access code '{code['code']}' deleted successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete access code: {str(e)}")
                else:
                    st.info("No access codes available. Create one above for students to use.")

                # Add new access code
                st.subheader("Create New Access Code")
                
                with st.form("add_code_form"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        new_code = st.text_input("New Access Code", placeholder="")
                    with col2:
                        max_uses = st.number_input("Max Uses", min_value=1, value=100, help="Leave empty for unlimited uses")
                    with col3:
                        submit_code = st.form_submit_button("➕ Create Code", use_container_width=True)
                    
                    if submit_code and new_code:
                        # Trim whitespace and validate
                        new_code = new_code.strip().upper()  # Convert to uppercase for consistency
                        if not new_code:
                            st.warning("Access code cannot be empty!")
                        elif len(new_code) < 3:
                            st.warning("Access code must be at least 3 characters long!")
                        elif not new_code.isalnum():
                            st.warning("Access code should only contain letters and numbers!")
                        else:
                            # Check if code already exists
                            existing_code = access_codes_collection.find_one({"code": new_code})
                            if existing_code:
                                st.warning(f"Access code '{new_code}' already exists!")
                            else:
                                # Insert the new access code
                                result = access_codes_collection.insert_one({
                                    "code": new_code,
                                    "created_at": time.time(),
                                    "educator_id": "Admin",
                                    "is_active": True,
                                    "max_uses": max_uses if max_uses > 0 else None,  # Unlimited uses if 0 or negative
                                    "description": f"Access code created by {st.session_state.get('username', 'Admin')}"
                                })
                                if result.inserted_id:
                                    st.success(f"✅ Access code '{new_code}' created successfully!")
                                    st.info(f"Students can now use this code: **{new_code}**")
                                    if max_uses and max_uses > 0:
                                        st.info(f"Maximum uses: {max_uses}")
                                    else:
                                        st.info("Unlimited uses allowed")
                                    st.rerun()
                                else:
                                    st.error("Failed to create access code. Please try again.")
        except Exception as e:
            st.error(f"An error occurred while accessing the database: {str(e)}")
            st.info("Please try refreshing the page or contact support if the issue persists.")

    elif page == "Beyond The Brush App":
        st.session_state.link_educator_active = True
        run_link_educator()




if __name__ == "__main__":
    admin_portal()