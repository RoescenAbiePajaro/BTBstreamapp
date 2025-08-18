import streamlit as st
import platform

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
    # Inject CSS to remove top margin/padding
    st.markdown(
        """
        <style>
        div.block-container {
            padding-top: 0rem;
        }
        h1 {
            margin-top: 0rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Beyond The Brush App Download")
    st.write("Download the latest version of Beyond The Brush")
    
    download_app()

    st.markdown("---")
    st.markdown("Guide Steps")
    st.markdown("""
    - **Step 1**: You are registered,next is to download the application by clicking the download button.
    - **Step 2**: When done downloading, open the application.
    - **Step 3**: Fill up information you registered and click on the enter button.
    """)
    
    st.markdown("---")
    st.markdown("System Requirements")
    st.markdown("""
    - **Webcam**: Required for hand tracking
    - **Internet Connection**: Required for initial setup and updates
    """)

if __name__ == "__main__":
    run_link()
