#!/usr/bin/env python3
"""
Quick Setup Script for Natural Language to SQL Dashboard
Run this after cloning the repository to set up the environment automatically.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            return True
        else:
            print(f"❌ {command}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {command}")
        print(f"Error: {e}")
        return False

def main():
    print("🚀 Setting up Natural Language to SQL Dashboard...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment
    print("\n📦 Creating virtual environment...")
    if not run_command("python -m venv .venv"):
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        activate_script = ".venv\\Scripts\\activate"
        pip_command = ".venv\\Scripts\\pip"
        python_command = ".venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        activate_script = "source .venv/bin/activate"
        pip_command = ".venv/bin/pip"
        python_command = ".venv/bin/python"
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command(f"{pip_command} install -r dashboard_app/requirements.txt"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Copy environment file
    print("\n⚙️ Setting up environment configuration...")
    env_example = Path("dashboard_app/backend/.env.example")
    env_file = Path("dashboard_app/backend/.env")
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
    else:
        print("ℹ️ .env file already exists")
    
    # Generate sample database (optional)
    print("\n🗄️ Checking for database...")
    if not Path("retail_database.db").exists():
        print("📊 Generating sample database (this may take a moment)...")
        if run_command(f"{python_command} data_processor.py"):
            print("✅ Sample database created")
        else:
            print("⚠️ Failed to create sample database (you can run data_processor.py manually later)")
    else:
        print("✅ Database already exists")
    
    # Setup complete
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit dashboard_app/backend/.env and add your GitHub token:")
    print("   GITHUB_TOKEN=your_actual_token_here")
    print("\n2. Start the backend server:")
    print("   cd dashboard_app/backend")
    if os.name == 'nt':
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("   python app.py")
    print("\n3. In a new terminal, start the frontend:")
    print("   cd dashboard_app/frontend")
    print("   python -m http.server 3000")
    print("\n4. Open http://localhost:3000 in your browser")
    print("\n🚀 Happy coding!")

if __name__ == "__main__":
    main()