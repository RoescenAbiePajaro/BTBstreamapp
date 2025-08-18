import streamlit as st
import os
import sys
import platform
import subprocess
from pathlib import Path


def download_app():
    st.markdown("### Download Beyond The Brush App")
    
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

def run_link_educator():
    """Main function to run the download interface"""
    st.title("Beyond The Brush App Download")
    st.write("Download the latest version of Beyond The Brush")
    
    download_app()
    st.markdown("---")
    st.markdown("Guide Steps")
    st.markdown("""
    - **Step 1**: Download the application by clicking the download button.
    - **Step 2**: When done dowloading,open the application.
    - **Step 3**: Enter Admin access code and click on the enter button.

    """)
    
    st.markdown("---")
    st.markdown("System Requirements")
    st.markdown("""
    - **Webcam**: Required for hand tracking
    - **Internet Connection**: Required for initial setup and updates
    """)

if __name__ == "__main__":
    run_link_educator()
