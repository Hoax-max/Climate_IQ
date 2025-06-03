#!/usr/bin/env python3
"""
Test script to verify Climate Action Intelligence Platform installation
"""
import sys
import os
import importlib
from pathlib import Path

def test_python_version():
    """Test Python version compatibility"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'requests',
        'dotenv',
        'langchain',
        'chromadb',
        'ibm_watsonx_ai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def test_project_structure():
    """Test project directory structure"""
    print("\n📁 Testing project structure...")
    
    required_dirs = [
        'backend',
        'backend/watsonx_integration',
        'backend/rag_system',
        'backend/api_handlers',
        'backend/data_processors',
        'frontend',
        'frontend/dashboard',
        'data'
    ]
    
    required_files = [
        'config.py',
        'requirements.txt',
        'run_app.py',
        'frontend/dashboard/main_app.py'
    ]
    
    missing_items = []
    
    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Missing")
            missing_items.append(dir_path)
    
    # Check files
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_items.append(file_path)
    
    return len(missing_items) == 0, missing_items

def test_environment_config():
    """Test environment configuration"""
    print("\n🔧 Testing environment configuration...")
    
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check for key environment variables
        with open('.env', 'r') as f:
            content = f.read()
            
        required_vars = [
            'IBM_CLOUD_API_KEY',
            'WATSONX_PROJECT_ID',
            'OPENWEATHER_API_KEY',
            'CARBON_INTERFACE_API_KEY'
        ]
        
        configured_vars = []
        for var in required_vars:
            if var in content and not content.split(var + '=')[1].split('\n')[0].strip() in ['', 'your_api_key', 'your_project_id']:
                configured_vars.append(var)
                print(f"✅ {var} - Configured")
            else:
                print(f"⚠️  {var} - Not configured (demo mode will be used)")
        
        return True, configured_vars
    else:
        print("⚠️  .env file not found - Demo mode will be used")
        return False, []

def test_backend_modules():
    """Test backend module imports"""
    print("\n🔧 Testing backend modules...")
    
    # Add backend to path
    sys.path.append(os.path.join(os.path.dirname(__file__)))
    
    modules_to_test = [
        ('config', 'Configuration'),
        ('backend.watsonx_integration.watsonx_client', 'WatsonX Client'),
        ('backend.rag_system.climate_rag', 'RAG System'),
        ('backend.api_handlers.climate_apis', 'Climate APIs'),
        ('backend.data_processors.impact_tracker', 'Impact Tracker')
    ]
    
    working_modules = []
    
    for module_name, display_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ {display_name}")
            working_modules.append(module_name)
        except Exception as e:
            print(f"❌ {display_name} - Error: {str(e)[:50]}...")
    
    return len(working_modules) == len(modules_to_test), working_modules

def main():
    """Run all tests"""
    print("🌍 Climate Action Intelligence Platform - Installation Test")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test Python version
    if not test_python_version():
        all_tests_passed = False
    
    # Test dependencies
    deps_ok, missing_deps = test_dependencies()
    if not deps_ok:
        all_tests_passed = False
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Run: pip install -r requirements.txt")
    
    # Test project structure
    struct_ok, missing_items = test_project_structure()
    if not struct_ok:
        all_tests_passed = False
        print(f"\n❌ Missing project items: {', '.join(missing_items)}")
    
    # Test environment configuration
    env_ok, configured_vars = test_environment_config()
    
    # Test backend modules
    modules_ok, working_modules = test_backend_modules()
    if not modules_ok:
        print("\n⚠️  Some backend modules have issues but demo mode should work")
    
    print("\n" + "=" * 60)
    
    if all_tests_passed:
        print("🎉 Installation test PASSED!")
        print("\n🚀 Ready to run: python run_app.py")
        
        if len(configured_vars) > 0:
            print(f"✅ Full functionality available with {len(configured_vars)} APIs configured")
        else:
            print("💡 Demo mode available (configure APIs in .env for full functionality)")
            
    else:
        print("❌ Installation test FAILED!")
        print("\n🔧 Please fix the issues above before running the application")
    
    print("\n📖 See README.md for detailed setup instructions")

if __name__ == "__main__":
    main()