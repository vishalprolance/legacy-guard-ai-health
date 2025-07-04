#!/usr/bin/env python3
"""
Setup script for Bank Application Health Check Automation
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_tesseract():
    """Install Tesseract OCR based on operating system"""
    system = platform.system().lower()
    
    print("🔧 Installing Tesseract OCR...")
    
    if system == "windows":
        print("📥 Please download and install Tesseract OCR manually:")
        print("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   2. Install to: C:\\Program Files\\Tesseract-OCR\\")
        print("   3. Add to PATH or update TESSERACT_CMD in .env file")
        
    elif system == "darwin":  # macOS
        try:
            subprocess.run(["brew", "install", "tesseract"], check=True)
            print("✅ Tesseract installed via Homebrew")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Tesseract. Please install Homebrew first:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            
    elif system == "linux":
        try:
            # Try apt-get first (Debian/Ubuntu)
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "tesseract-ocr"], check=True)
            print("✅ Tesseract installed via apt-get")
        except subprocess.CalledProcessError:
            try:
                # Try yum (RHEL/CentOS)
                subprocess.run(["sudo", "yum", "install", "-y", "tesseract"], check=True)
                print("✅ Tesseract installed via yum")
            except subprocess.CalledProcessError:
                print("❌ Failed to install Tesseract automatically")
                print("   Please install manually: sudo apt-get install tesseract-ocr")

def install_python_packages():
    """Install Python packages from requirements.txt"""
    print("📦 Installing Python packages...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Python packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'logs',
        'reports',
        'screenshots', 
        'baseline',
        'baseline/elements',
        'reports/visual_diffs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   Created: {directory}")
    
    print("✅ Directories created")

def setup_environment_file():
    """Setup environment configuration file"""
    print("⚙️ Setting up environment configuration...")
    
    if not os.path.exists('.env'):
        try:
            # Copy .env.example to .env
            with open('.env.example', 'r') as source:
                content = source.read()
            
            with open('.env', 'w') as target:
                target.write(content)
            
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your specific configuration")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
    else:
        print("✅ .env file already exists")

def create_sample_baseline():
    """Create sample baseline images directory structure"""
    print("🖼️ Setting up baseline images structure...")
    
    baseline_readme = """# Baseline Images

This directory contains baseline screenshots for visual comparison testing.

## Structure:
- dashboard.png - Main dashboard screenshot
- login.png - Login screen screenshot  
- transactions.png - Transaction screen screenshot
- elements/ - Individual UI element templates

## Usage:
1. Run the health check once to capture initial screenshots
2. Review and approve the screenshots
3. Copy approved screenshots to this baseline directory
4. Future runs will compare against these baselines

## Updating Baselines:
When the application UI changes intentionally:
1. Capture new screenshots
2. Review for correctness
3. Replace the corresponding baseline images
4. Document the changes in your change log
"""
    
    try:
        with open('baseline/README.md', 'w') as f:
            f.write(baseline_readme)
        print("✅ Created baseline README")
    except Exception as e:
        print(f"❌ Failed to create baseline README: {e}")

def run_health_check():
    """Run a test health check to verify setup"""
    print("🏥 Running test health check...")
    
    try:
        # Import and run a basic configuration test
        from crew_main import BankAppHealthChecker
        
        print("✅ Core modules imported successfully")
        
        # Test configuration loading
        health_checker = BankAppHealthChecker()
        print("✅ Configuration loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        print("   This might be expected if the bank application is not available")
        return False

def main():
    """Main setup function"""
    print("🚀 Bank Application Health Check Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install Tesseract OCR
    install_tesseract()
    
    # Install Python packages
    if not install_python_packages():
        print("❌ Setup failed during package installation")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup environment file
    setup_environment_file()
    
    # Create sample baseline structure
    create_sample_baseline()
    
    # Test the setup
    setup_success = run_health_check()
    
    print("\n" + "=" * 50)
    if setup_success:
        print("✅ Setup completed successfully!")
    else:
        print("⚠️ Setup completed with warnings")
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your specific configuration")
    print("2. Update config/confluence_flows.json with your test flows")
    print("3. Install Tesseract OCR if not done automatically")
    print("4. Run: python crew_main.py")
    print("\n🔧 For Windows users:")
    print("   - Ensure the bank application path in .env is correct")
    print("   - Update TESSERACT_CMD path in .env if needed")
    print("   - Test with: python -c \"import pytesseract; print('OCR available')\"")

if __name__ == "__main__":
    main()