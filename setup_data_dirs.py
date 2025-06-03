#!/usr/bin/env python3
"""
Setup script to create necessary data directories for the Climate Action Intelligence Platform
"""

import os
import json
from pathlib import Path

def create_data_directories():
    """Create all necessary data directories"""
    
    # Define directory structure
    directories = [
        "data",
        "data/user_profiles",
        "data/local_data", 
        "data/climate_vectordb"
    ]
    
    print("🌍 Setting up Climate Action Intelligence Platform data directories...")
    print("=" * 60)
    
    # Create directories
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    # Create placeholder files to ensure directories are tracked
    placeholder_files = {
        "data/user_profiles/.gitkeep": "# User profiles will be stored here\n",
        "data/local_data/.gitkeep": "# Local climate data cache will be stored here\n", 
        "data/climate_vectordb/.gitkeep": "# ChromaDB vector database will be stored here\n"
    }
    
    for file_path, content in placeholder_files.items():
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Created: {file_path}")
    
    # Create sample user profile for demo
    sample_profile = {
        "user_id": "demo_user",
        "location": "New York, NY",
        "lifestyle": "Urban",
        "interests": ["Energy Efficiency", "Transportation", "Renewable Energy"],
        "budget_range": "moderate",
        "created_at": "2025-06-02",
        "actions_completed": [],
        "impact_metrics": {
            "co2_saved": 0,
            "money_saved": 0,
            "actions_count": 0
        }
    }
    
    with open("data/user_profiles/demo_user.json", 'w') as f:
        json.dump(sample_profile, f, indent=2)
    print("✅ Created: data/user_profiles/demo_user.json")
    
    print("\n" + "=" * 60)
    print("🎉 Data directories setup complete!")
    print("\n📁 Directory structure:")
    print("data/")
    print("├── user_profiles/     # User profile data")
    print("├── local_data/        # Climate data cache") 
    print("└── climate_vectordb/  # Vector database storage")
    print("\n🚀 Ready to run: python run_app.py")

if __name__ == "__main__":
    create_data_directories()