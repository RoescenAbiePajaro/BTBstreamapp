from streamlit.web import cli
import sys
import os
import webbrowser
import time
import threading

# --- FORCE STREAMLIT PORT ---
FORCED_PORT = "8501"
os.environ["STREAMLIT_SERVER_PORT"] = FORCED_PORT

def open_browser():
    """Open browser after a short delay to ensure Streamlit is running"""
    time.sleep(3)  # Wait for Streamlit to start
    try:
        webbrowser.open(f'http://localhost:{FORCED_PORT}')
        print(f"Browser opened automatically on port {FORCED_PORT}!")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print(f"Please manually open: http://localhost:{FORCED_PORT}")

if __name__ == '__main__':
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)
        
        print(f"Starting Streamlit app on port {FORCED_PORT}...")
        print(f"Local URL: http://localhost:{FORCED_PORT}")
        
        # Start browser opening in background thread
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # Run the Streamlit app with forced port
        sys.argv = [
            'streamlit', 'run', 'app.py',
            '--server.port', FORCED_PORT,
            '--server.headless', 'true',  # Run in headless mode for exe
            '--browser.gatherUsageStats', 'false'
        ]
        cli.main()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
