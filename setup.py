#!/usr/bin/env python3
"""
Setup Script untuk Advanced Pterodactyl Backup Bot
Membantu instalasi dan konfigurasi otomatis
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path

class BotSetup:
    def __init__(self):
        self.config_file = "config.py"
        self.requirements_file = "requirements.txt"
        self.main_file = "main.py"
        
    def print_banner(self):
        """Print banner setup"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🤖 Advanced Pterodactyl Backup Bot - Setup Wizard        ║
║                                                              ║
║    Memudahkan instalasi dan konfigurasi bot backup          ║
║    untuk server Pterodactyl pribadi Anda                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_python_version(self):
        """Check Python version"""
        print("🔍 Checking Python version...")
        
        if sys.version_info < (3, 7):
            print("❌ Python 3.7+ required!")
            print(f"   Current version: {sys.version}")
            return False
        
        print(f"✅ Python version OK: {sys.version.split()[0]}")
        return True
    
    def install_requirements(self):
        """Install required packages"""
        print("\n📦 Installing required packages...")
        
        requirements = [
            "python-telegram-bot==20.7",
            "requests==2.31.0"
        ]
        
        try:
            # Create requirements.txt if needed
            if not os.path.exists(self.requirements_file):
                with open(self.requirements_file, 'w') as f:
                    f.write('\n'.join(requirements))
                print(f"✅ Created {self.requirements_file}")
            
            # Install packages
            result = subprocess.run([
                sys.executable, "-m", "pip", "install"] + requirements, 
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("✅ All packages installed successfully!")
                return True
            else:
                print(f"❌ Error installing packages: {result.stderr}")
                print("Trying alternative installation method...")
                
                # Try installing from requirements.txt
                result2 = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", self.requirements_file], 
                    capture_output=True, text=True
                )
                
                if result2.returncode == 0:
                    print("✅ Packages installed using requirements.txt!")
                    return True
                else:
                    print(f"❌ Alternative installation also failed: {result2.stderr}")
                    return False
                
        except Exception as e:
            print(f"❌ Exception during installation: {e}")
            return False
    
    def test_imports(self):
        """Test if required modules can be imported"""
        print("\n🧪 Testing imports...")
        
        required_modules = [
            'telegram',
            'requests',
            'asyncio',
            'json',
            'os',
            'logging'
        ]
        
        failed_imports = []
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError as e:
                print(f"❌ {module}: {e}")
                failed_imports.append(module)
        
        if failed_imports:
            print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
            print("Please install missing packages manually:")
            for module in failed_imports:
                if module == 'telegram':
                    print("   pip install python-telegram-bot")
                else:
                    print(f"   pip install {module}")
            return False
        
        print("✅ All required modules imported successfully!")
        return True
    
    def check_config_file(self):
        """Check if config file exists and is valid"""
        print("\n📋 Checking configuration file...")
        
        if not os.path.exists(self.config_file):
            print(f"❌ {self.config_file} not found!")
            return False
        
        try:
            # Try to import config
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", self.config_file)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            # Check required attributes
            required_attrs = [
                'PTERODACTYL_DOMAIN',
                'PTERODACTYL_API_KEY',
                'PTERODACTYL_CLIENT_API_KEY',
                'TELEGRAM_BOT_TOKEN'
            ]
            
            missing_attrs = []
            for attr in required_attrs:
                if not hasattr(config_module.Config, attr):
                    missing_attrs.append(attr)
            
            if missing_attrs:
                print(f"❌ Missing required config attributes: {', '.join(missing_attrs)}")
                return False
            
            print("✅ Configuration file is valid!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading config file: {e}")
            return False
    
    def test_pterodactyl_connection(self):
        """Test connection to Pterodactyl panel"""
        print("\n🔗 Testing Pterodactyl connection...")
        
        try:
            # Import config
            from config import Config
            
            headers = {
                'Authorization': f'Bearer {Config.PTERODACTYL_API_KEY}',
                'Content-Type': 'application/json',
                'Accept': 'Application/vnd.pterodactyl.v1+json'
            }
            
            response = requests.get(
                f"{Config.PTERODACTYL_DOMAIN}/api/application/servers", 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                servers = response.json()['data']
                print(f"✅ Pterodactyl connection successful! Found {len(servers)} servers.")
                return True
            else:
                print(f"❌ Pterodactyl connection failed! Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ Pterodactyl connection error: {e}")
            return False
    
    def test_telegram_bot(self):
        """Test Telegram bot token"""
        print("\n📱 Testing Telegram bot...")
        
        try:
            from config import Config
            
            response = requests.get(
                f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getMe", 
                timeout=10
            )
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info['ok']:
                    bot_data = bot_info['result']
                    print(f"✅ Telegram bot valid!")
                    print(f"   Bot Name: {bot_data['first_name']}")
                    print(f"   Username: @{bot_data.get('username', 'N/A')}")
                    print(f"   Bot ID: {bot_data['id']}")
                    return True
            
            print("❌ Invalid Telegram bot token!")
            print(f"   Response: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ Telegram bot test error: {e}")
            return False
    
    def create_run_script(self):
        """Create run script untuk memudahkan eksekusi"""
        print("\n📝 Creating run scripts...")
        
        # Windows batch script
        bat_content = '''@echo off
title Advanced Pterodactyl Backup Bot
color 0a

echo.
echo ========================================
echo    Advanced Pterodactyl Backup Bot
echo ========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.7+ first.
    pause
    exit /b 1
)

if not exist config.py (
    echo ❌ config.py not found!
    echo Please make sure config.py exists and is configured properly.
    pause
    exit /b 1
)

echo 🚀 Starting bot...
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Bot stopped with error!
    pause
)

echo.
echo Bot stopped.
pause'''
        
        # Linux/Mac shell script
        sh_content = '''#!/bin/bash

echo "========================================="
echo "   Advanced Pterodactyl Backup Bot"
echo "========================================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.7+ first."
    exit 1
fi

# Check config
if [ ! -f "config.py" ]; then
    echo "❌ config.py not found!"
    echo "Please make sure config.py exists and is configured properly."
    exit 1
fi

echo "🚀 Starting bot..."
echo

python3 main.py

echo
echo "Bot stopped."
'''
        
        try:
            # Create Windows script
            with open('run.bat', 'w') as f:
                f.write(bat_content)
            print("✅ Created run.bat for Windows")
            
            # Create Unix script
            with open('run.sh', 'w') as f:
                f.write(sh_content)
            
            # Make shell script executable
            import stat
            os.chmod('run.sh', stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
            print("✅ Created run.sh for Linux/Mac")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating run scripts: {e}")
            return False
    
    def show_next_steps(self):
        """Show next steps to user"""
        print("\n" + "=" * 60)
        print("🎉 SETUP VALIDATION COMPLETED!")
        print("=" * 60)
        
        print("\n📋 Next Steps:")
        print("1. Run the bot:")
        if os.name == 'nt':  # Windows
            print("   run.bat")
            print("   atau")
            print("   python main.py")
        else:  # Unix-like
            print("   ./run.sh")
            print("   atau")
            print("   python3 main.py")
        
        print("\n2. Setup bot di Telegram:")
        print("   • Buka chat dengan bot Anda")
        print("   • Ketik /start")
        print("   • Klik 'Setup Chat Log'")
        print("   • Ikuti instruksi selanjutnya")
        
        print("\n3. Mulai backup:")
        print("   • Gunakan 'Quick Scan' untuk test")
        print("   • Review hasil scan")
        print("   • Klik 'Start Backup' untuk backup")
        
        print("\n📁 Files in project:")
        print("   • main.py - Bot utama")
        print("   • config.py - Konfigurasi")
        print("   • requirements.txt - Dependencies")
        print("   • run.bat / run.sh - Run scripts")
        
        print("\n⚠️  Important reminders:")
        print("   • Jangan share config.py (berisi API keys)")
        print("   • Bot akan menghapus direktori setelah backup")
        print("   • Test di development server dulu")
        
        print("\n📚 Commands setelah bot jalan:")
        print("   /start - Interactive menu")
        print("   /scan - Full server scan")
        print("   /stats - Usage statistics")
        print("   /clean - Clear scan cache")
        
        print("\n✨ Your bot is ready to use! ✨")
    
    def run_setup(self):
        """Run complete setup validation"""
        self.print_banner()
        
        # Check requirements
        if not self.check_python_version():
            return False
        
        # Install packages
        if not self.install_requirements():
            print("\n⚠️  Package installation failed, but continuing...")
        
        # Test imports
        if not self.test_imports():
            print("\n❌ Import test failed! Please fix import issues first.")
            return False
        
        # Check config file
        if not self.check_config_file():
            print("\n❌ Config file validation failed!")
            print("Please ensure config.py exists and is properly configured.")
            return False
        
        # Test connections
        pterodactyl_ok = self.test_pterodactyl_connection()
        telegram_ok = self.test_telegram_bot()
        
        if not pterodactyl_ok:
            print("\n⚠️  Pterodactyl connection failed!")
            print("Please check your domain and API keys in config.py")
        
        if not telegram_ok:
            print("\n⚠️  Telegram bot test failed!")
            print("Please check your bot token in config.py")
        
        # Create run scripts
        self.create_run_script()
        
        # Show results
        if pterodactyl_ok and telegram_ok:
            print("\n✅ All tests passed!")
        else:
            print("\n⚠️  Some tests failed, but bot may still work.")
            print("Please fix the issues above for optimal performance.")
        
        # Show next steps
        self.show_next_steps()
        
        return True

def main():
    """Main setup function"""
    setup = BotSetup()
    
    try:
        success = setup.run_setup()
        if success:
            print("\n🎯 Setup validation completed!")
            sys.exit(0)
        else:
            print("\n❌ Setup validation failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()