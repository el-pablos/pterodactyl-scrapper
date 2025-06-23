#!/usr/bin/env python3
"""
Test Connectivity Script
Tes koneksi ke Pterodactyl dan Telegram untuk debugging
"""

import requests
import json
from datetime import datetime

def test_pterodactyl():
    """Test Pterodactyl API connection"""
    print("🔗 Testing Pterodactyl Connection...")
    print("-" * 40)
    
    try:
        from config import Config
        
        # Test Application API
        headers = {
            'Authorization': f'Bearer {Config.PTERODACTYL_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'Application/vnd.pterodactyl.v1+json'
        }
        
        print(f"Domain: {Config.PTERODACTYL_DOMAIN}")
        print(f"API Key: {Config.PTERODACTYL_API_KEY[:10]}...{Config.PTERODACTYL_API_KEY[-10:]}")
        
        # Test servers endpoint
        response = requests.get(
            f"{Config.PTERODACTYL_DOMAIN}/api/application/servers",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            servers = data['data']
            print(f"✅ SUCCESS: Found {len(servers)} servers")
            
            if servers:
                print("\n📋 Server List:")
                for i, server in enumerate(servers[:5], 1):  # Show first 5
                    print(f"  {i}. {server['attributes']['name']} (ID: {server['attributes']['identifier']})")
                if len(servers) > 5:
                    print(f"  ... and {len(servers) - 5} more servers")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except ImportError:
        print("❌ config.py not found or invalid!")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

def test_telegram():
    """Test Telegram Bot API"""
    print("📱 Testing Telegram Bot...")
    print("-" * 40)
    
    try:
        from config import Config
        
        print(f"Bot Token: {Config.TELEGRAM_BOT_TOKEN[:10]}...{Config.TELEGRAM_BOT_TOKEN[-10:]}")
        
        # Test getMe endpoint
        response = requests.get(
            f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getMe",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_info = data['result']
                print("✅ SUCCESS: Bot is valid")
                print(f"Bot Name: {bot_info['first_name']}")
                print(f"Username: @{bot_info.get('username', 'N/A')}")
                print(f"Bot ID: {bot_info['id']}")
                print(f"Can Join Groups: {bot_info.get('can_join_groups', False)}")
                print(f"Can Read Messages: {bot_info.get('can_read_all_group_messages', False)}")
            else:
                print(f"❌ FAILED: {data['description']}")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            
    except ImportError:
        print("❌ config.py not found or invalid!")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

def test_client_api():
    """Test Pterodactyl Client API"""
    print("🔐 Testing Pterodactyl Client API...")
    print("-" * 40)
    
    try:
        from config import Config
        
        headers = {
            'Authorization': f'Bearer {Config.PTERODACTYL_CLIENT_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'Application/vnd.pterodactyl.v1+json'
        }
        
        print(f"Client API Key: {Config.PTERODACTYL_CLIENT_API_KEY[:10]}...{Config.PTERODACTYL_CLIENT_API_KEY[-10:]}")
        
        # Test client servers endpoint
        response = requests.get(
            f"{Config.PTERODACTYL_DOMAIN}/api/client",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Client API is working")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except ImportError:
        print("❌ config.py not found or invalid!")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

def test_file_operations():
    """Test file operations on first server"""
    print("📁 Testing File Operations...")
    print("-" * 40)
    
    try:
        from config import Config
        
        # Get first server
        app_headers = {
            'Authorization': f'Bearer {Config.PTERODACTYL_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'Application/vnd.pterodactyl.v1+json'
        }
        
        servers_response = requests.get(
            f"{Config.PTERODACTYL_DOMAIN}/api/application/servers",
            headers=app_headers,
            timeout=10
        )
        
        if servers_response.status_code != 200:
            print("❌ Cannot get servers list")
            return
        
        servers = servers_response.json()['data']
        if not servers:
            print("❌ No servers found")
            return
        
        first_server = servers[0]
        server_id = first_server['attributes']['identifier']
        server_name = first_server['attributes']['name']
        
        print(f"Testing with server: {server_name} ({server_id})")
        
        # Test file listing
        client_headers = {
            'Authorization': f'Bearer {Config.PTERODACTYL_CLIENT_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'Application/vnd.pterodactyl.v1+json'
        }
        
        files_response = requests.get(
            f"{Config.PTERODACTYL_DOMAIN}/api/client/servers/{server_id}/files/list",
            headers=client_headers,
            timeout=10
        )
        
        print(f"File List Status: {files_response.status_code}")
        
        if files_response.status_code == 200:
            files_data = files_response.json()['data']
            print(f"✅ SUCCESS: Found {len(files_data)} files/directories")
            
            # Look for target file
            target_found = False
            for file_item in files_data:
                if file_item['attributes']['name'] == Config.TARGET_FILENAME:
                    target_found = True
                    print(f"🎯 Found target file: {Config.TARGET_FILENAME}")
                    print(f"   Size: {file_item['attributes']['size']} bytes")
                    print(f"   Modified: {file_item['attributes']['modified_at']}")
                    break
            
            if not target_found:
                print(f"⚠️  Target file '{Config.TARGET_FILENAME}' not found in root directory")
                
        else:
            print(f"❌ FAILED: {files_response.status_code}")
            print(f"Response: {files_response.text[:200]}...")
            
    except ImportError:
        print("❌ config.py not found or invalid!")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

def main():
    """Main test function"""
    print("🧪 CONNECTIVITY TEST SCRIPT")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    test_pterodactyl()
    test_telegram()
    test_client_api()
    test_file_operations()
    
    print("=" * 50)
    print("🎯 Test completed!")
    print()
    print("💡 Tips:")
    print("- If Pterodactyl tests fail, check domain and API keys")
    print("- If Telegram test fails, check bot token from @BotFather")
    print("- If Client API fails, check client API permissions")
    print("- If file operations fail, ensure servers are online")

if __name__ == "__main__":
    main()