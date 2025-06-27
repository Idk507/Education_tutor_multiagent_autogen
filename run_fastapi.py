#!/usr/bin/env python3
"""
Startup script for the Educational Tutor FastAPI application
"""

import os
import sys
import uvicorn
from pathlib import Path

def setup_environment():
    """Set up environment variables and paths"""
    # Ensure Docker is disabled for AutoGen
    os.environ["AUTOGEN_USE_DOCKER"] = "False"
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    print("🔧 Environment configured")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "autogen",
        "langchain",
        "openai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install dependencies:")
        print("   pip install -r requirements_fastapi.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def run_server(host="127.0.0.1", port=8000, reload=True):
    """Run the FastAPI server"""
    print(f"🚀 Starting Educational Tutor API Server")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   API Docs: http://{host}:{port}/docs")
    print(f"   Health Check: http://{host}:{port}/")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🎓 Educational Tutor FastAPI Server")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Parse command line arguments (simple version)
    host = "127.0.0.1"
    port = 8000
    reload = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--production":
            reload = False
            print("🏭 Running in production mode (no auto-reload)")
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python run_fastapi.py                 # Development mode with auto-reload")
            print("  python run_fastapi.py --production    # Production mode")
            print("  python run_fastapi.py --help          # Show this help")
            return
    
    # Run the server
    run_server(host=host, port=port, reload=reload)

if __name__ == "__main__":
    main() 