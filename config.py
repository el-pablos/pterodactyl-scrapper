# config.py - Bot Configuration
# Template konfigurasi untuk Pterodactyl Backup Bot

class Config:
    # ===== PTERODACTYL CONFIGURATION =====
    PTERODACTYL_DOMAIN = 'https://two.ndikafath.store'
    PTERODACTYL_API_KEY = 'ptla_c1JhPVcR94oM9WhEQVp6vnSj402lpKVOBSJFTcUBMpm'
    PTERODACTYL_CLIENT_API_KEY = 'ptlc_9yFJ5hMKa7Q8rm35j8gH3rVQrGgwZjONr1krUSqr6Wd'
    
    # ===== SERVER CONFIGURATION =====
    EGGS_ID = '15'
    LOCATION_ID = '1'
    
    # ===== TELEGRAM BOT CONFIGURATION =====
    TELEGRAM_BOT_TOKEN = '7537447390:AAEilfvUBGfh9yEecAS6hURVI_gyYjfBtR8'
    
    # ===== BACKUP CONFIGURATION =====
    TARGET_FILENAME = 'creds.json'
    AUTO_DELETE_AFTER_BACKUP = True
    BACKUP_FILE_PREFIX = 'creds_backup'
    
    # ===== SCAN CONFIGURATION =====
    SCAN_SUBDIRECTORIES = True
    MAX_SCAN_DEPTH = 3
    SCAN_TIMEOUT = 30
    
    # ===== LOGGING CONFIGURATION =====
    LOG_LEVEL = 'INFO'
    LOG_TO_FILE = True
    LOG_FILENAME = 'bot_backup.log'
    
    # ===== SECURITY CONFIGURATION =====
    ALLOWED_USERS = []  # Empty = allow all users
    ADMIN_USER_ID = None
    
    # ===== ADVANCED CONFIGURATION =====
    MAX_CONCURRENT_SCANS = 5
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 5

def validate_config():
    """Validate configuration"""
    required_configs = [
        'PTERODACTYL_DOMAIN',
        'PTERODACTYL_API_KEY', 
        'PTERODACTYL_CLIENT_API_KEY',
        'TELEGRAM_BOT_TOKEN'
    ]
    
    for config_name in required_configs:
        if not getattr(Config, config_name) or getattr(Config, config_name) == '':
            raise ValueError(f"Configuration {config_name} must be filled!")
    
    return True