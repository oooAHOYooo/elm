#!/usr/bin/env python3
"""
Development server launcher for Elm City Daily
This script starts the Flask app in debug mode with auto-reload
"""
import os
import sys
import subprocess

def main():
    # Check if we're in a virtual environment
    venv_python = os.path.join('.venv', 'Scripts', 'python.exe')
    if os.path.exists(venv_python):
        python_cmd = venv_python
        print("✓ Using virtual environment")
    else:
        python_cmd = sys.executable
        print("⚠ Using system Python (consider creating a venv)")
    
    # Set environment variables for development
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    
    print("\n" + "="*60)
    print("ELM CITY DAILY - DEVELOPMENT SERVER")
    print("="*60)
    print(f"Python: {python_cmd}")
    print(f"Starting Flask app in debug mode...")
    print(f"Server will be available at: http://127.0.0.1:5000")
    print(f"\nPress CTRL+C to stop the server")
    print("="*60 + "\n")
    
    try:
        # Run the app with debug mode
        subprocess.run(
            [python_cmd, 'app.py', '--debug'],
            env=env,
            check=True
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
