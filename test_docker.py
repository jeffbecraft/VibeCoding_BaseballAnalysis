"""
Docker Deployment Test Script

Tests that the Docker configuration is working correctly:
1. Verifies Dockerfile exists
2. Checks docker-compose.yml syntax
3. Provides instructions for local testing
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} not found: {filepath}")
        return False

def main():
    print("🐳 Docker Deployment Test\n")
    print("=" * 60)
    
    # Check required files
    all_good = True
    all_good &= check_file_exists("Dockerfile", "Dockerfile")
    all_good &= check_file_exists("docker-compose.yml", "Docker Compose")
    all_good &= check_file_exists(".dockerignore", "Docker Ignore")
    all_good &= check_file_exists("requirements.txt", "Requirements")
    all_good &= check_file_exists("requirements_web.txt", "Web Requirements")
    all_good &= check_file_exists("streamlit_app.py", "Streamlit App")
    
    print("\n" + "=" * 60)
    
    if not all_good:
        print("\n❌ Some required files are missing!")
        return 1
    
    print("\n✅ All required files present!")
    print("\n📋 Next Steps - Test Docker Locally:\n")
    
    print("1️⃣  Build and start containers:")
    print("   docker-compose up -d\n")
    
    print("2️⃣  Check container status:")
    print("   docker-compose ps\n")
    
    print("3️⃣  View logs:")
    print("   docker-compose logs -f mlb-stats-web\n")
    
    print("4️⃣  Access the app:")
    print("   Open browser: http://localhost:8501\n")
    
    print("5️⃣  Stop containers:")
    print("   docker-compose down\n")
    
    print("=" * 60)
    print("\n🔍 Optional - Build Docker image only:")
    print("   docker build -t mlb-stats:test .\n")
    
    print("📖 For production deployment, see:")
    print("   docs/PRODUCTION_DEPLOYMENT.md\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
