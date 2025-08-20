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
        courses_collection = db["courses"]
        blocks_collection = db["blocks"]
        year_levels_collection = db["year_levels"]
        yield students_collection, access_codes_collection, courses_collection, blocks_collection, year_levels_collection
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

def manage_courses():
    st.subheader("Manage Courses")
    with get_mongodb_connection() as (_, _, courses_collection, _, _):
        # Display existing courses
        courses = list(courses_collection.find())
        
        if courses:
            for course in courses:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.write(f"**{course['name']}**")
                with col2:
                    if st.button(f"Edit {course['name']}", key=f"edit_course_{course['_id']}"):
                        st.session_state['editing_course'] = course['_id']
                with col3:
                    if st.button(f"Delete {course['name']}", key=f"delete_course_{course['_id']}"):
                        courses_collection.delete_one({"_id": course["_id"]})
                        st.rerun()

            # Show edit form if a course is being edited
            if 'editing_course' in st.session_state:
                course_to_edit = next((c for c in courses if c['_id'] == st.session_state['editing_course']), None)
                if course_to_edit:
                    with st.form(key=f"edit_course_form_{course_to_edit['_id']}"):
                        new_name = st.text_input("Course Name", value=course_to_edit['name'])
                        submit_edit = st.form_submit_button("Save Changes")
                        cancel_edit = st.form_submit_button("Cancel")

                        if submit_edit and new_name:
                            courses_collection.update_one(
                                {"_id": course_to_edit["_id"]},
                                {"$set": {"name": new_name}}
                            )
                            del st.session_state['editing_course']
                            st.success("Course updated successfully!")
                            st.rerun()

                        if cancel_edit:
                            del st.session_state['editing_course']
                            st.rerun()
        else:
            st.info("No courses available.")

        # Add new course
        with st.form("add_course_form"):
            new_course = st.text_input("New Course Name")
            submit_course = st.form_submit_button("Add Course")
            
            if submit_course and new_course:
                if not new_course.strip():
                    st.warning("Course name cannot be empty!")
                else:
                    # Check if course already exists
                    existing_course = courses_collection.find_one({"name": new_course.strip()})
                    if existing_course:
                        st.warning(f"Course '{new_course}' already exists!")
                    else:
                        courses_collection.insert_one({"name": new_course.strip()})
                        st.success(f"Course '{new_course}' added successfully!")
                        st.rerun()

def manage_blocks():
    st.subheader("Manage Blocks")
    with get_mongodb_connection() as (_, _, _, blocks_collection, _):
        # Display existing blocks
        blocks = list(blocks_collection.find())
        
        if blocks:
            for block in blocks:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.write(f"**{block['name']}**")
                with col2:
                    if st.button(f"Edit {block['name']}", key=f"edit_block_{block['_id']}"):
                        st.session_state['editing_block'] = block['_id']
                with col3:
                    if st.button(f"Delete {block['name']}", key=f"delete_block_{block['_id']}"):
                        blocks_collection.delete_one({"_id": block["_id"]})
                        st.rerun()

            # Show edit form if a block is being edited
            if 'editing_block' in st.session_state:
                block_to_edit = next((b for b in blocks if b['_id'] == st.session_state['editing_block']), None)
                if block_to_edit:
                    with st.form(key=f"edit_block_form_{block_to_edit['_id']}"):
                        new_name = st.text_input("Block Name", value=block_to_edit['name'])
                        submit_edit = st.form_submit_button("Save Changes")
                        cancel_edit = st.form_submit_button("Cancel")

                        if submit_edit and new_name:
                            blocks_collection.update_one(
                                {"_id": block_to_edit["_id"]},
                                {"$set": {"name": new_name}}
                            )
                            del st.session_state['editing_block']
                            st.success("Block updated successfully!")
                            st.rerun()

                        if cancel_edit:
                            del st.session_state['editing_block']
                            st.rerun()
        else:
            st.info("No blocks available.")

        # Add new block
        with st.form("add_block_form"):
            new_block = st.text_input("New Block Name")
            submit_block = st.form_submit_button("Add Block")
            
            if submit_block and new_block:
                if not new_block.strip():
                    st.warning("Block name cannot be empty!")
                else:
                    # Check if block already exists
                    existing_block = blocks_collection.find_one({"name": new_block.strip()})
                    if existing_block:
                        st.warning(f"Block '{new_block}' already exists!")
                    else:
                        blocks_collection.insert_one({"name": new_block.strip()})
                        st.success(f"Block '{new_block}' added successfully!")
                        st.rerun()

def manage_year_levels():
    st.subheader("Manage Year Levels")
    with get_mongodb_connection() as (_, _, _, _, year_levels_collection):
        # Display existing year levels
        year_levels = list(year_levels_collection.find())
        
        if year_levels:
            for level in year_levels:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.write(f"**{level['name']}**")
                with col2:
                    if st.button(f"Edit {level['name']}", key=f"edit_level_{level['_id']}"):
                        st.session_state['editing_level'] = level['_id']
                with col3:
                    if st.button(f"Delete {level['name']}", key=f"delete_level_{level['_id']}"):
                        year_levels_collection.delete_one({"_id": level["_id"]})
                        st.rerun()

            # Show edit form if a year level is being edited
            if 'editing_level' in st.session_state:
                level_to_edit = next((l for l in year_levels if l['_id'] == st.session_state['editing_level']), None)
                if level_to_edit:
                    with st.form(key=f"edit_level_form_{level_to_edit['_id']}"):
                        new_name = st.text_input("Year Level Name", value=level_to_edit['name'])
                        submit_edit = st.form_submit_button("Save Changes")
                        cancel_edit = st.form_submit_button("Cancel")

                        if submit_edit and new_name:
                            year_levels_collection.update_one(
                                {"_id": level_to_edit["_id"]},
                                {"$set": {"name": new_name}}
                            )
                            del st.session_state['editing_level']
                            st.success("Year level updated successfully!")
                            st.rerun()

                        if cancel_edit:
                            del st.session_state['editing_level']
                            st.rerun()
        else:
            st.info("No year levels available.")

        # Add new year level
        with st.form("add_level_form"):
            new_level = st.text_input("New Year Level Name")
            submit_level = st.form_submit_button("Add Year Level")
            
            if submit_level and new_level:
                if not new_level.strip():
                    st.warning("Year level name cannot be empty!")
                else:
                    # Check if year level already exists
                    existing_level = year_levels_collection.find_one({"name": new_level.strip()})
                    if existing_level:
                        st.warning(f"Year level '{new_level}' already exists!")
                    else:
                        year_levels_collection.insert_one({"name": new_level.strip()})
                        st.success(f"Year level '{new_level}' added successfully!")
                        st.rerun()

def admin_portal():
    # Check authentication state
    if not st.session_state.get('authenticated') or st.session_state.get('user_type') != 'educator':
        st.error("Access denied. Please login as an educator.")
        st.stop()

    # Initialize session state for navigation if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Student Registrations"

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "Student Registrations", 
        "Access Codes", 
        "Manage Courses",
        "Manage Blocks",
        "Manage Year Levels",
        "Beyond The Brush App"
    ])

    # Update current page in session state
    st.session_state.current_page = page

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

        with get_mongodb_connection() as (students_collection, _, courses_collection, blocks_collection, year_levels_collection):
            # Add search and filter section
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                search_query = st.text_input("🔍 Search students by name", "")
            
            # Get all available options for filters
            courses = ["All"] + [course["name"] for course in courses_collection.find()]
            blocks = ["All"] + [block["name"] for block in blocks_collection.find()]
            year_levels = ["All"] + [level["name"] for level in year_levels_collection.find()]
            
            with col2:
                course_filter = st.selectbox("Filter by Course", courses)
            with col3:
                block_filter = st.selectbox("Filter by Block", blocks)
            with col4:
                year_filter = st.selectbox("Filter by Year Level", year_levels)

            # Build query based on filters
            query = {}
            if search_query:
                query["name"] = {"$regex": search_query, "$options": "i"}  # Case-insensitive search
            if course_filter != "All":
                query["course"] = course_filter
            if block_filter != "All":
                query["block"] = block_filter
            if year_filter != "All":
                query["year_level"] = year_filter

            # Display all registered students with filters applied
            students = list(students_collection.find(query))

            if students:
                st.write(f"Found {len(students)} student(s)")
                for student in students:
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        st.write(f"**{student['name']}**")
                        st.caption(f"Course: {student.get('course', 'N/A')} | Block: {student.get('block', 'N/A')} | Year: {student.get('year_level', 'N/A')}")
                        st.caption(f"Registered: {time.ctime(student['registered_at'])}")
                    with col2:
                        if st.button(f"Edit {student['name']}", key=f"edit_{student['_id']}"):
                            st.session_state['editing_student'] = student['_id']
                    with col3:
                        if st.button(f"Delete {student['name']}", key=f"delete_{student['_id']}"):
                            students_collection.delete_one({"_id": student["_id"]})
                            st.rerun()

                # Show edit form if a student is being edited
                if 'editing_student' in st.session_state:
                    student_to_edit = next((s for s in students if s['_id'] == st.session_state['editing_student']), None)
                    if student_to_edit:
                        with get_mongodb_connection() as (_, _, courses_collection, blocks_collection, year_levels_collection):
                            with st.form(key=f"edit_form_{student_to_edit['_id']}"):
                                new_name = st.text_input("New Name", value=student_to_edit['name'])
                                
                                # Get current options
                                current_courses = [course["name"] for course in courses_collection.find()]
                                current_blocks = [block["name"] for block in blocks_collection.find()]
                                current_year_levels = [level["name"] for level in year_levels_collection.find()]
                                
                                # Create dropdowns with current values
                                new_course = st.selectbox(
                                    "Course", 
                                    options=current_courses,
                                    index=current_courses.index(student_to_edit.get('course', current_courses[0])) if student_to_edit.get('course') in current_courses else 0
                                )
                                new_block = st.selectbox(
                                    "Block", 
                                    options=current_blocks,
                                    index=current_blocks.index(student_to_edit.get('block', current_blocks[0])) if student_to_edit.get('block') in current_blocks else 0
                                )
                                new_year = st.selectbox(
                                    "Year Level", 
                                    options=current_year_levels,
                                    index=current_year_levels.index(student_to_edit.get('year_level', current_year_levels[0])) if student_to_edit.get('year_level') in current_year_levels else 0
                                )
                                
                                submit_edit = st.form_submit_button("Save Changes")
                                cancel_edit = st.form_submit_button("Cancel")

                                if submit_edit and new_name:
                                    students_collection.update_one(
                                        {"_id": student_to_edit["_id"]},
                                        {"$set": {
                                            "name": new_name,
                                            "course": new_course,
                                            "block": new_block,
                                            "year_level": new_year
                                        }}
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
            with get_mongodb_connection() as (students_collection, access_codes_collection, _, _, _):
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
                            
                            # Show code type (admin or student)
                            code_type = "🔑 Admin" if code.get('is_admin_code', False) else "👨‍🎓 Student"
                            st.write(code_type)
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
                
                with st.form("add_code_form", clear_on_submit=True):
                    # Use container for better styling
                    with st.container():
                        # Adjust column ratios for better spacing
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            new_code = st.text_input(
                                "Access Code", 
                                placeholder="Enter code (min. 3 chars)",
                                help="Code must be at least 3 characters long"
                            )
                            is_admin_code = st.checkbox(
                                "Make this an admin code", 
                                help="Check this for educator/admin access only",
                                key="admin_code_checkbox"
                            )
                        
                        with col2:
                            max_uses = st.number_input(
                                "Maximum Uses", 
                                min_value=1, 
                                value=100,
                                help="Maximum number of times this code can be used"
                            )
                            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                            submit_code = st.form_submit_button(
                                "Create Access Code",
                                use_container_width=True,
                                type="primary"
                            )

                    # Rest of validation code remains the same
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
                                    "is_admin_code": is_admin_code,
                                    "max_uses": max_uses if max_uses > 0 else None,  # Unlimited uses if 0 or negative
                                    "description": f"Access code created by {st.session_state.get('username', 'Admin')}"
                                })
                                if result.inserted_id:
                                    st.success(f"✅ Access code '{new_code}' created successfully!")
                                    st.info(f"Code type: {'🔑 Admin' if is_admin_code else '👨‍🎓 Student'}")
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

    elif page == "Manage Courses":
        st.session_state.link_educator_active = False
        st.title("Course Management")
        manage_courses()

    elif page == "Manage Blocks":
        st.session_state.link_educator_active = False
        st.title("Block Management")
        manage_blocks()

    elif page == "Manage Year Levels":
        st.session_state.link_educator_active = False
        st.title("Year Level Management")
        manage_year_levels()

    elif page == "Beyond The Brush App":
        st.session_state.link_educator_active = True
        run_link_educator()

if __name__ == "__main__":
    admin_portal()