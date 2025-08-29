import streamlit as st
import os
import sys
import platform
import subprocess
from pathlib import Path

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

def download_app():
    
    system = platform.system()
    if system == "Windows":
        file_name = "BeyondTheBrush_Windows.exe"
        button_text = "Download Now"
    elif system == "Darwin":  # macOS
        file_name = "BeyondTheBrush_macOS.dmg"
        button_text = "Download for macOS"
    elif system == "Linux":
        file_name = "BeyondTheBrush_Linux"
        button_text = "Download for Linux"
    else:
        st.error("Unsupported operating system")
        return
    
    # This would be the URL to your actual hosted file
    download_url = f"https://your-download-url.com/{file_name}"
    
    st.markdown(
        f"""
        <a href="{download_url}" download>
            <button style="background-color: #4CAF50; color: white; padding: 10px 20px; 
                         border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">
                {button_text}
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

def run_link():
    """Main function to run the download interface"""
    st.title("Beyond The Brush")
    
    
    
    # Create three columns with a gap in the middle
    col1, gap, col2 = st.columns([2, 1, 3])
    
    # Left column with Lite version content
    with col1:
        st.subheader("Beyond The Brush Lite")
        lite_app_url = "https://btbreact.onrender.com"  # Replace with your actual URL
        st.markdown(
            f"""
            <a href="{lite_app_url}">
                <button style="background-color: #008CBA; color: white; padding: 10px 20px; 
                             border: none; border-radius: 4px; cursor: pointer; font-size: 16px;
                             margin: 10px 0;">
                    Launch Web App
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )
        
        # Add two images (replace with your actual image paths)
        st.image("b23fd125-0ed9-4166-8579-c2c46f5f6e8e.jpg", caption="Lite App Preview 1")
        st.image("a59dd5c2-4116-4d40-a47f-d9f5cae88698.jpg", caption="Lite App Preview 2")
        

      
        
        st.markdown("---")
        st.markdown("Guide Steps")
        st.markdown("""
        - **Step 1**: Click the Launch Web App button
        - **Step 2**: No download required
        - **Step 3**: Enter name and Student access code and click on the enter button
        """)
        
        st.markdown("---")
        st.markdown("System Requirements")
        st.markdown("""
        - **Webcam**: Required for hand tracking
        - **Internet Connection**: Required for operation
        - **Browser**: Latest version of Chrome, Firefox, or Edge
        """)
    
    # Middle gap column (empty)
    with gap:
        st.write("")  # Empty space for gap
    
    # Right column with Desktop app content
    with col2:
        st.subheader("Beyond The Brush Desktop App")
        
        download_app()

        video_file = open('abeyond.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)
        
        st.markdown("---")
        st.markdown("Guide Steps")
        st.markdown("""
        - **Step 1**: Download the application by clicking the download button.
        - **Step 2**: When done downloading, open the application.
        - **Step 3**: Enter name and Student access code and click on the enter button.
        """)
        
        st.markdown("---")
        st.markdown("System Requirements")
        st.markdown("""
        - **Webcam**: Required for hand tracking
        - **Internet Connection**: Required for initial setup and updates
        """)

if __name__ == "__main__":
    run_link()