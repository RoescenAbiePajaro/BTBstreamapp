import streamlit as st
import os
import sys
import platform
import subprocess
from pathlib import Path


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
        lite_app_url = "https://your-lite-app-url.com"  # Replace with your actual URL
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
        st.image("image1.jpg", caption="Lite App Preview 1")
        st.image("image2.jpg", caption="Lite App Preview 2")
        

      
        
        st.markdown("---")
        st.markdown("Guide Steps")
        st.markdown("""
        - **Step 1**: Click the Launch Web App button
        - **Step 2**: No download required
        - **Step 3**: Enter Educator access code and click on the enter button
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
        - **Step 3**: Enter Educator access code and click on the enter button.
        """)
        
        st.markdown("---")
        st.markdown("System Requirements")
        st.markdown("""
        - **Webcam**: Required for hand tracking
        - **Internet Connection**: Required for initial setup and updates
        - **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
        """)

if __name__ == "__main__":
    run_link()