#!/usr/bin/env python3
"""
Educational Tutor Application Startup Script
This script helps you run both the FastAPI backend and React frontend.
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                    Educational Tutor System                       ║
    ║                    AI-Powered Learning Platform                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Check if required dependencies are available"""
    print("🔍 Checking requirements...")
    
    # Check Python packages
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'autogen-agentchat', 
        'langchain', 'openai', 'tenacity'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing Python packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements_fastapi.txt'
            ])
            print("✅ Python packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Python packages. Please run:")
            print("   pip install -r requirements_fastapi.txt")
            return False
    else:
        print("✅ All Python packages are available")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js is available: {result.stdout.strip()}")
        else:
            print("❌ Node.js is not available. Please install Node.js from https://nodejs.org/")
            return False
    except FileNotFoundError:
        print("❌ Node.js is not installed. Please install Node.js from https://nodejs.org/")
        return False
    
    return True

def setup_frontend():
    """Set up the React frontend"""
    frontend_dir = Path('frontend')
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    print("📦 Setting up React frontend...")
    
    # Check if node_modules exists
    if not (frontend_dir / 'node_modules').exists():
        print("📥 Installing frontend dependencies...")
        try:
            subprocess.check_call(['npm', 'install'], cwd=frontend_dir)
            print("✅ Frontend dependencies installed!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return False
    else:
        print("✅ Frontend dependencies already installed")
    
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend...")
    try:
        # Use the run_fastapi.py script if it exists, otherwise use uvicorn directly
        if os.path.exists('run_fastapi.py'):
            subprocess.Popen([sys.executable, 'run_fastapi.py'])
        else:
            subprocess.Popen([
                sys.executable, '-m', 'uvicorn', 
                'app:app', 
                '--host', '127.0.0.1', 
                '--port', '8000', 
                '--reload'
            ])
        print("✅ FastAPI backend started on http://127.0.0.1:8000")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the React frontend"""
    print("🚀 Starting React frontend...")
    frontend_dir = Path('frontend')
    
    try:
        # Set environment variable for API URL
        env = os.environ.copy()
        env['REACT_APP_API_URL'] = 'http://127.0.0.1:8000'
        
        subprocess.Popen(['npm', 'start'], cwd=frontend_dir, env=env)
        print("✅ React frontend started on http://localhost:3000")
        return True
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def wait_for_backend():
    """Wait for backend to be ready"""
    import requests
    
    print("⏳ Waiting for backend to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get('http://127.0.0.1:8000/', timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        time.sleep(1)
    
    print("⚠️ Backend might not be ready, but continuing...")
    return False

def open_browser():
    """Open the application in the default browser"""
    print("🌐 Opening application in browser...")
    time.sleep(3)  # Wait a bit for frontend to start
    webbrowser.open('http://localhost:3000')

def main():
    """Main function to start the application"""
    print_banner()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py') and not os.path.exists('agent.py'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    print("\n🎯 Starting Educational Tutor Application...")
    print("=" * 60)
    
    # Start backend
    if not start_backend():
        print("❌ Failed to start backend")
        sys.exit(1)
    
    # Wait for backend to be ready
    wait_for_backend()
    
    # Start frontend
    if not start_frontend():
        print("❌ Failed to start frontend")
        sys.exit(1)
    
    # Open browser
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.start()
    
    print("\n" + "=" * 60)
    print("🎉 Educational Tutor Application is starting!")
    print("📖 Backend API: http://127.0.0.1:8000")
    print("🌐 Frontend UI: http://localhost:3000")
    print("📚 API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the application")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Educational Tutor Application...")
        print("Thank you for using the Educational Tutor System!")

if __name__ == "__main__":
    main() 