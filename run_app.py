#!/usr/bin/env python3
"""
Launch script for Climate Action Intelligence Platform
"""
import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import ibm_watsonx_ai
        import chromadb
        import sentence_transformers
        import plotly
        import pandas
        import requests
        logger.info("✅ All dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    logger.info("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    directories = [
        "data/climate_vectordb",
        "data/user_profiles",
        "data/local_data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Created directory: {directory}")

def check_environment():
    """Check environment variables"""
    required_vars = [
        "IBM_CLOUD_API_KEY",
        "WATSONX_PROJECT_ID",
        "OPENWEATHER_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️  Missing environment variables: {missing_vars}")
        logger.info("💡 Make sure your .env file is properly configured")
    else:
        logger.info("✅ Environment variables are configured")
    
    return len(missing_vars) == 0

def run_streamlit_app():
    """Run the Streamlit application"""
    logger.info("🚀 Starting Climate Action Intelligence Platform...")
    
    # Change to the correct directory
    app_path = "frontend/dashboard/main_app.py"
    
    if not os.path.exists(app_path):
        logger.error(f"❌ Application file not found: {app_path}")
        return False
    
    try:
        # Run Streamlit with proper configuration
        cmd = [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port=12000",
            "--server.address=0.0.0.0",
            "--server.headless=true",
            "--server.enableCORS=true",
            "--server.enableXsrfProtection=false",
            "--browser.gatherUsageStats=false"
        ]
        
        logger.info("🌐 Application will be available at:")
        logger.info("   Local: http://localhost:12000")
        logger.info("   Network: https://work-1-fvctichmsizgqcpl.prod-runtime.all-hands.dev")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        logger.info("👋 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Error running application: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🌍 Climate Action Intelligence Platform")
    print("=" * 50)
    
    # Setup directories
    setup_directories()
    
    # Check environment
    env_ok = check_environment()
    
    # Check dependencies
    if not check_dependencies():
        logger.info("📦 Installing missing dependencies...")
        if not install_dependencies():
            logger.error("❌ Failed to install dependencies. Please install manually:")
            logger.error("   pip install -r requirements.txt")
            return 1
    
    # Run the application
    if not run_streamlit_app():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())