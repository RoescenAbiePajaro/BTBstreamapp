from streamlit.web import cli
import sys
import os

if __name__ == '__main__':
    try:
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Working directory: {current_dir}")
        
        # Change to the current directory
        os.chdir(current_dir)
        
        print("Starting Streamlit app...")
        print("Browser will open automatically when app.py loads...")
        print("Using configuration from .streamlit/config.toml")
        
        # Run the streamlit app - app.py will handle browser opening
        # Don't pass server arguments since they're in config.toml
        sys.argv = [
            'streamlit', 'run', 'app.py'
        ]
        
        cli.main()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Press Enter to exit...")
        input()
        sys.exit(1)