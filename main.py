import os
import json
import requests
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import concurrent.futures
from pathlib import Path
import io

# Import konfigurasi
try:
    from config import Config, validate_config
except ImportError:
    print("❌ File config.py tidak ditemukan!")
    print("📝 Silakan buat file config.py berdasarkan template yang disediakan")
    exit(1)

class AdvancedPterodactylBackupBot:
    def __init__(self):
        # Validasi konfigurasi
        validate_config()
        
        # Load konfigurasi
        self.domain = Config.PTERODACTYL_DOMAIN
        self.apikey = Config.PTERODACTYL_API_KEY
        self.capikey = Config.PTERODACTYL_CLIENT_API_KEY
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.eggs_id = Config.EGGS_ID
        self.location_id = Config.LOCATION_ID
        
        # Pengaturan backup
        self.target_filename = Config.TARGET_FILENAME
        self.auto_delete = Config.AUTO_DELETE_AFTER_BACKUP
        self.backup_prefix = Config.BACKUP_FILE_PREFIX
        
        # Pengaturan scan
        self.scan_subdirs = Config.SCAN_SUBDIRECTORIES
        self.max_depth = Config.MAX_SCAN_DEPTH
        self.scan_timeout = Config.SCAN_TIMEOUT
        
        # Setup logging
        self.setup_logging()
        
        # Storage
        self.log_chat_id = None
        self.scan_results = {}
        self.load_persistent_data()
        
        # Headers API
        self.headers = {
            'Authorization': f'Bearer {self.apikey}',
            'Content-Type': 'application/json',
            'Accept': 'Application/vnd.pterodactyl.v1+json'
        }
        
        self.client_headers = {
            'Authorization': f'Bearer {self.capikey}',
            'Content-Type': 'application/json',
            'Accept': 'Application/vnd.pterodactyl.v1+json'
        }
        
        # Stats
        self.stats = {
            'total_scans': 0,
            'total_backups': 0,
            'total_deletions': 0,
            'last_scan': None,
            'last_backup': None
        }
    def setup_logging(self):
        """Setup logging system"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Clear existing handlers to avoid duplicates
        logging.getLogger().handlers.clear()
        
        # Setup level
        level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
        
        # Setup handlers
        handlers = [logging.StreamHandler()]
        
        if Config.LOG_TO_FILE:
            handlers.append(logging.FileHandler(Config.LOG_FILENAME, encoding='utf-8'))
        
        logging.basicConfig(
            format=log_format,
            level=level,
            handlers=handlers,
            force=True
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🤖 Advanced Pterodactyl Backup Bot initialized")

    def load_persistent_data(self):
        """Load data persisten dari file"""
        try:
            if os.path.exists('bot_data.json'):
                with open('bot_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.log_chat_id = data.get('log_chat_id')
                    self.stats = data.get('stats', self.stats)
                    self.scan_results = data.get('scan_results', {})
                    self.logger.info("📊 Persistent data loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading persistent data: {e}")

    def save_persistent_data(self):
        """Simpan data persisten ke file"""
        try:
            data = {
                'log_chat_id': self.log_chat_id,
                'stats': self.stats,
                'scan_results': self.scan_results
            }
            with open('bot_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving persistent data: {e}")

    def check_user_permission(self, user_id: int) -> bool:
        """Cek apakah user diizinkan menggunakan bot"""
        if not Config.ALLOWED_USERS:  # Jika list kosong, izinkan semua
            return True
        return user_id in Config.ALLOWED_USERS
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk command /start"""
        user_id = update.effective_user.id
        
        if not self.check_user_permission(user_id):
            await update.message.reply_text("❌ Anda tidak memiliki akses untuk menggunakan bot ini.")
            return
        
        keyboard = [
            [InlineKeyboardButton("🔧 Setup Chat Log", callback_data="setup_log")],
            [InlineKeyboardButton("🔍 Quick Scan", callback_data="quick_scan")],
            [InlineKeyboardButton("📊 Status Bot", callback_data="bot_status")],
            [InlineKeyboardButton("📖 Help", callback_data="show_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = f"""
🤖 **Advanced Pterodactyl Backup Bot**
*Versi 2.0 - Enhanced Edition*

Selamat datang, {update.effective_user.first_name}! 
Bot ini telah diupgrade dengan fitur-fitur canggih untuk backup otomatis file `{self.target_filename}` dari server Pterodactyl Anda.

**✨ Fitur Baru:**
• Scan concurrent untuk performa optimal
• Backup incremental dengan timestamp
• Advanced logging dan monitoring
• Interactive keyboard untuk navigasi mudah
• Statistics dan reporting lengkap
• Error handling yang lebih robust

Pilih opsi di bawah untuk memulai:
        """
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk inline keyboard buttons"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        if not self.check_user_permission(user_id):
            await query.edit_message_text("❌ Anda tidak memiliki akses untuk menggunakan bot ini.")
            return
        
        if query.data == "setup_log":
            await self.setup_log_callback(query, context)
        elif query.data == "quick_scan":
            await self.quick_scan_callback(query, context)
        elif query.data == "bot_status":
            await self.status_callback(query, context)
        elif query.data == "show_help":
            await self.help_callback(query, context)
        elif query.data == "start_backup":
            await self.backup_callback(query, context)
        elif query.data.startswith("confirm_backup_"):
            scan_id = query.data.replace("confirm_backup_", "")
            await self.confirm_backup_callback(query, context, scan_id)
        elif query.data == "cancel_backup":
            await self.cancel_backup_callback(query, context)
    async def setup_log_callback(self, query, context):
        """Setup chat log melalui callback"""
        self.log_chat_id = query.message.chat_id
        self.save_persistent_data()
        
        await query.edit_message_text(
            f"✅ Chat log berhasil disetup!\n\n"
            f"📍 Chat ID: `{self.log_chat_id}`\n"
            f"📁 File backup akan dikirim ke chat ini.\n\n"
            f"🚀 Bot siap digunakan!",
            parse_mode='Markdown'
        )

    async def quick_scan_callback(self, query, context):
        """Quick scan melalui callback"""
        if not self.log_chat_id:
            await query.edit_message_text(
                "❌ Chat log belum disetup!\n"
                "Silakan setup terlebih dahulu dengan klik tombol Setup Chat Log."
            )
            return
        
        await query.edit_message_text("🔍 Memulai quick scan...")
        await self.perform_scan(query, context, quick_mode=True)

    async def status_callback(self, query, context):
        """Status callback"""
        uptime = "Active"  # Bisa dihitung dari start time
        
        status_msg = f"""
📊 **Status Bot Backup**

🔧 **Konfigurasi:**
• Domain: `{self.domain}`
• Target File: `{self.target_filename}`
• Auto Delete: {'✅' if self.auto_delete else '❌'}
• Scan Subdirs: {'✅' if self.scan_subdirs else '❌'}

💬 **Telegram:**
• Log Chat: {'✅ Setup' if self.log_chat_id else '❌ Belum setup'}
• Uptime: {uptime}

📈 **Statistics:**
• Total Scans: {self.stats['total_scans']}
• Total Backups: {self.stats['total_backups']}
• Total Deletions: {self.stats['total_deletions']}
• Last Scan: {self.stats['last_scan'] or 'Never'}

🎯 **Status:** {'🟢 Ready' if self.log_chat_id else '🟡 Need Setup'}
        """
        
        keyboard = [[InlineKeyboardButton("🔄 Refresh", callback_data="bot_status")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            status_msg,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    async def help_callback(self, query, context):
        """Help callback"""
        help_msg = """
📖 **Panduan Penggunaan Bot**

**🎯 Perintah Utama:**
• `/start` - Menu utama bot
• `/scan` - Scan lengkap semua server
• `/stats` - Statistik penggunaan
• `/clean` - Bersihkan cache scan

**🔄 Workflow Normal:**
1. Setup chat log di menu utama
2. Jalankan scan untuk cari file
3. Review hasil scan
4. Backup file yang ditemukan
5. Konfirmasi penghapusan direktori

**⚠️ Peringatan:**
• Bot akan menghapus direktori setelah backup
• Pastikan file backup sudah diterima sebelum konfirmasi
• Gunakan dengan hati-hati di production

**🛠️ Troubleshooting:**
• Pastikan API key valid
• Cek koneksi internet
• Verifikasi permission server
        """
        
        await query.edit_message_text(help_msg, parse_mode='Markdown')

    async def get_servers_async(self) -> List[Dict]:
        """Get servers secara asynchronous"""
        try:
            url = f"{self.domain}/api/application/servers"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data['data']
            else:
                self.logger.error(f"Error getting servers: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Exception getting servers: {e}")
            return []

    def run_scan_server_sync(self, server_id: str, server_name: str) -> List[Dict]:
        """Synchronous wrapper untuk scan server - digunakan di ThreadPoolExecutor"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.scan_server_files(server_id, server_name))
            loop.close()
            return result
        except Exception as e:
            self.logger.error(f"Error in sync wrapper for server {server_name}: {e}")
            return []
    async def scan_server_files(self, server_id: str, server_name: str) -> List[Dict]:
        """Scan files in a server"""
        found_files = []
        
        try:
            # Scan root directory
            files = await self.get_server_files_async(server_id, "/")
            
            for file_item in files:
                if (file_item['attributes']['is_file'] and 
                    file_item['attributes']['name'] == self.target_filename):
                    
                    found_files.append({
                        'server_id': server_id,
                        'server_name': server_name,
                        'file_path': file_item['attributes']['name'],
                        'directory': '/',
                        'size': file_item['attributes']['size'],
                        'modified_at': file_item['attributes']['modified_at']
                    })
            
            # Scan subdirectories if enabled
            if self.scan_subdirs:
                found_files.extend(
                    await self.scan_subdirectories(server_id, server_name, files, depth=1)
                )
        
        except Exception as e:
            self.logger.error(f"Error scanning server {server_name}: {e}")
        
        return found_files

    async def scan_subdirectories(self, server_id: str, server_name: str, 
                                files: List[Dict], depth: int) -> List[Dict]:
        """Recursively scan subdirectories"""
        found_files = []
        
        if depth > self.max_depth:
            return found_files
        
        for file_item in files:
            if not file_item['attributes']['is_file']:  # It's a directory
                subdir_path = file_item['attributes']['name']
                
                try:
                    subfiles = await self.get_server_files_async(server_id, f"/{subdir_path}")
                    
                    for subfile in subfiles:
                        if (subfile['attributes']['is_file'] and 
                            subfile['attributes']['name'] == self.target_filename):
                            
                            found_files.append({
                                'server_id': server_id,
                                'server_name': server_name,
                                'file_path': f"{subdir_path}/{subfile['attributes']['name']}",
                                'directory': f"/{subdir_path}",
                                'size': subfile['attributes']['size'],
                                'modified_at': subfile['attributes']['modified_at']
                            })
                    
                    # Recursive scan
                    if depth < self.max_depth:
                        found_files.extend(
                            await self.scan_subdirectories(
                                server_id, server_name, subfiles, depth + 1
                            )
                        )
                
                except Exception as e:
                    self.logger.warning(f"Error scanning subdirectory {subdir_path}: {e}")
        
        return found_files
    async def get_server_files_async(self, server_id: str, path: str = "/") -> List[Dict]:
        """Get files from server asynchronously with retry mechanism"""
        max_retries = Config.RETRY_ATTEMPTS
        retry_delay = Config.RETRY_DELAY
        
        for attempt in range(max_retries):
            try:
                url = f"{self.domain}/api/client/servers/{server_id}/files/list"
                params = {'directory': path} if path != "/" else {}
                
                self.logger.debug(f"Attempting to get files from server {server_id}, attempt {attempt + 1}")
                
                response = requests.get(
                    url, 
                    headers=self.client_headers, 
                    params=params,
                    timeout=self.scan_timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['data']
                elif response.status_code == 500:
                    self.logger.warning(f"Server {server_id} returned 500 error (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        self.logger.info(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry

    async def perform_scan(self, update_obj, context, quick_mode=False):
        """Perform comprehensive scan"""
        self.logger.info("Starting server scan...")
        
        # Update stats
        self.stats['total_scans'] += 1
        self.stats['last_scan'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Get servers
            servers = await self.get_servers_async()
            
            if not servers:
                await update_obj.edit_message_text("❌ Tidak dapat mengambil daftar server.")
                return
            
            # Progress message
            progress_msg = f"🔍 Scanning {len(servers)} servers...\n\n"
            await update_obj.edit_message_text(progress_msg)
            
            # Sequential scanning untuk menghindari masalah concurrency
            all_found_files = []
            
            for i, server in enumerate(servers, 1):
                server_id = server['attributes']['identifier']
                server_name = server['attributes']['name']
                
                try:
                    # Update progress
                    progress = (i / len(servers)) * 100
                    progress_msg = f"🔍 Scanning server {i}/{len(servers)}: {server_name}\n"
                    progress_msg += f"📊 Progress: {progress:.1f}%\n"
                    progress_msg += f"📄 Found files: {len(all_found_files)}"
                    
                    await update_obj.edit_message_text(progress_msg)
                    
                    # Scan server
                    found_files = await self.scan_server_files(server_id, server_name)
                    all_found_files.extend(found_files)
                    
                except Exception as e:
                    self.logger.error(f"Error scanning server {server_name}: {e}")
            
            # Save scan results
            scan_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.scan_results[scan_id] = {
                'timestamp': datetime.now().isoformat(),
                'found_files': all_found_files,
                'total_servers': len(servers),
                'quick_mode': quick_mode
            }
            
            self.save_persistent_data()
            
            # Generate results message
            if all_found_files:
                result_msg = f"✅ **Scan Completed!**\n\n"
                result_msg += f"🎯 Found {len(all_found_files)} files:\n\n"
                
                for i, file_info in enumerate(all_found_files[:10], 1):  # Show first 10
                    result_msg += f"{i}. **{file_info['server_name']}**\n"
                    result_msg += f"   📁 Path: `{file_info['file_path']}`\n"
                    result_msg += f"   📊 Size: {file_info['size']} bytes\n\n"
                
                if len(all_found_files) > 10:
                    result_msg += f"... and {len(all_found_files) - 10} more files\n\n"
                
                # Add backup button
                keyboard = [[InlineKeyboardButton("🚀 Start Backup", callback_data="start_backup")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                context.user_data['current_scan_id'] = scan_id
                
            else:
                result_msg = f"❌ No `{self.target_filename}` files found in any server."
                reply_markup = None
            
            await update_obj.edit_message_text(
                result_msg,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error during scan: {e}")
            await update_obj.edit_message_text(f"❌ Error during scan: {str(e)}")
    async def backup_callback(self, query, context):
        """Backup files callback"""
        scan_id = context.user_data.get('current_scan_id')
        
        if not scan_id or scan_id not in self.scan_results:
            await query.edit_message_text("❌ No scan results found. Please run a scan first.")
            return
        
        scan_data = self.scan_results[scan_id]
        found_files = scan_data['found_files']
        
        # Show confirmation message with details
        confirm_msg = f"""
⚠️ **KONFIRMASI BACKUP**

🔍 **Hasil Scan:**
• Total files ditemukan: {len(found_files)}
• Auto-delete direktori: {'✅ Enabled' if self.auto_delete else '❌ Disabled'}

📂 **Files yang akan di-backup:**
"""
        
        for i, file_info in enumerate(found_files[:5], 1):  # Show first 5
            confirm_msg += f"{i}. {file_info['server_name']}: `{file_info['file_path']}`\n"
        
        if len(found_files) > 5:
            confirm_msg += f"... dan {len(found_files) - 5} file lainnya\n"
        
        if self.auto_delete:
            confirm_msg += "\n⚠️ **PERINGATAN:** Direktori akan dihapus setelah backup!"
        
        confirm_msg += "\n\nApakah Anda yakin ingin melanjutkan?"
        
        keyboard = [
            [InlineKeyboardButton("✅ Ya, Lanjutkan", callback_data=f"confirm_backup_{scan_id}")],
            [InlineKeyboardButton("❌ Batal", callback_data="cancel_backup")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            confirm_msg,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def confirm_backup_callback(self, query, context, scan_id):
        """Konfirmasi backup dan mulai proses"""
        if scan_id not in self.scan_results:
            await query.edit_message_text("❌ Scan results not found!")
            return
        
        scan_data = self.scan_results[scan_id]
        found_files = scan_data['found_files']
        
        await query.edit_message_text("🚀 Starting backup process...")
        await self.perform_backup(query, context, found_files)

    async def cancel_backup_callback(self, query, context):
        """Cancel backup process"""
        await query.edit_message_text("❌ Backup dibatalkan oleh user.")

    async def perform_backup(self, update_obj, context, found_files):
        """Perform backup of found files"""
        self.logger.info(f"Starting backup of {len(found_files)} files...")
        
        success_count = 0
        error_count = 0
        deleted_dirs = []
        
        for i, file_info in enumerate(found_files, 1):
            try:
                # Progress update
                progress_msg = f"📤 Backing up file {i}/{len(found_files)}\n"
                progress_msg += f"🖥️ Server: {file_info['server_name']}\n"
                progress_msg += f"📁 File: {file_info['file_path']}"
                
                await update_obj.edit_message_text(progress_msg)
                
                # Download file
                file_content = await self.download_file_async(
                    file_info['server_id'], 
                    file_info['file_path']
                )
                
                if file_content:
                    # Generate backup filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"{self.backup_prefix}_{file_info['server_name']}_{timestamp}.json"
                    
                    # Create file-like object
                    file_obj = io.BytesIO(file_content)
                    file_obj.name = backup_filename
                    
                    # Send to log chat
                    await context.bot.send_document(
                        chat_id=self.log_chat_id,
                        document=file_obj,
                        filename=backup_filename,
                        caption=f"📤 **Backup Complete**\n\n"
                               f"🖥️ Server: `{file_info['server_name']}`\n"
                               f"📁 Original Path: `{file_info['file_path']}`\n"
                               f"📅 Backup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                               f"📊 File Size: {file_info['size']} bytes",
                        parse_mode='Markdown'
                    )
                    
                    # Delete directory if auto-delete is enabled
                    if self.auto_delete and file_info['directory'] not in deleted_dirs:
                        delete_success = await self.delete_directory_async(
                            file_info['server_id'], 
                            file_info['directory']
                        )
                        
                        if delete_success:
                            deleted_dirs.append(file_info['directory'])
                            self.stats['total_deletions'] += 1
                    
                    success_count += 1
                    self.stats['total_backups'] += 1
                    
                else:
                    error_count += 1
                    self.logger.error(f"Failed to download {file_info['file_path']}")
                
            except Exception as e:
                error_count += 1
                self.logger.error(f"Error backing up {file_info['file_path']}: {e}")
        
        # Update stats
        self.stats['last_backup'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_persistent_data()
        
        # Final report
        final_msg = f"""
🎉 **Backup Process Complete!**

✅ **Successfully backed up:** {success_count} files
❌ **Errors:** {error_count} files
📂 **Total processed:** {len(found_files)} files

📊 **Actions taken:**
• Files downloaded and sent to log chat
• Directories deleted: {len(deleted_dirs)} {'(Auto-delete enabled)' if self.auto_delete else '(Auto-delete disabled)'}

📬 All backup files have been sent to your log chat.
        """
        
        await update_obj.edit_message_text(final_msg, parse_mode='Markdown')
    async def download_file_async(self, server_id: str, file_path: str) -> Optional[bytes]:
        """Download file from server asynchronously"""
        try:
            url = f"{self.domain}/api/client/servers/{server_id}/files/download"
            payload = {'file': file_path}
            
            response = requests.post(
                url, 
                headers=self.client_headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                download_data = response.json()
                download_url = download_data['attributes']['url']
                
                # Download actual file content
                file_response = requests.get(download_url, timeout=30)
                if file_response.status_code == 200:
                    return file_response.content
            
            return None
        except Exception as e:
            self.logger.error(f"Exception downloading file {file_path}: {e}")
            return None

    async def delete_directory_async(self, server_id: str, directory_path: str) -> bool:
        """Delete directory from server asynchronously"""
        try:
            url = f"{self.domain}/api/client/servers/{server_id}/files/delete"
            payload = {
                'root': '/',
                'files': [directory_path.lstrip('/')]
            }
            
            response = requests.post(
                url, 
                headers=self.client_headers, 
                json=payload,
                timeout=30
            )
            
            return response.status_code == 204
        except Exception as e:
            self.logger.error(f"Exception deleting directory {directory_path}: {e}")
            return False

    # Command handlers
    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command handler untuk /scan"""
        user_id = update.effective_user.id
        if not self.check_user_permission(user_id):
            await update.message.reply_text("❌ Anda tidak memiliki akses untuk menggunakan bot ini.")
            return
        
        if not self.log_chat_id:
            await update.message.reply_text("❌ Chat log belum disetup! Gunakan /start untuk setup.")
            return
        
        message = await update.message.reply_text("🔍 Starting comprehensive scan...")
        await self.perform_scan(message, context, quick_mode=False)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command handler untuk /stats"""
        user_id = update.effective_user.id
        if not self.check_user_permission(user_id):
            await update.message.reply_text("❌ Anda tidak memiliki akses untuk menggunakan bot ini.")
            return
        
        stats_msg = f"""
📈 **Detailed Statistics**

🔢 **Usage Stats:**
• Total Scans Performed: {self.stats['total_scans']}
• Total Files Backed Up: {self.stats['total_backups']}
• Total Directories Deleted: {self.stats['total_deletions']}

📅 **Timeline:**
• Last Scan: {self.stats['last_scan'] or 'Never'}
• Last Backup: {self.stats['last_backup'] or 'Never'}

💾 **Scan History:**
• Cached Scan Results: {len(self.scan_results)}

⚙️ **Configuration:**
• Target Filename: `{self.target_filename}`
• Auto Delete: {'Enabled' if self.auto_delete else 'Disabled'}
• Subdirectory Scan: {'Enabled' if self.scan_subdirs else 'Disabled'}
• Max Scan Depth: {self.max_depth}
• Concurrent Scans: {Config.MAX_CONCURRENT_SCANS}
        """
        
        await update.message.reply_text(stats_msg, parse_mode='Markdown')

    async def clean_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command handler untuk /clean - Bersihkan cache scan"""
        user_id = update.effective_user.id
        if not self.check_user_permission(user_id):
            await update.message.reply_text("❌ Anda tidak memiliki akses untuk menggunakan bot ini.")
            return
        
        # Clear scan results
        cleared_count = len(self.scan_results)
        self.scan_results.clear()
        self.save_persistent_data()
        
        await update.message.reply_text(
            f"🧹 **Cache Cleared!**\n\n"
            f"✅ Cleared {cleared_count} cached scan results\n"
            f"💾 Persistent data updated",
            parse_mode='Markdown'
        )

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log errors caused by Updates."""
        self.logger.error('Exception while handling an update:', exc_info=context.error)
        
        # Try to inform user about error
        try:
            if update and hasattr(update, 'effective_chat') and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Terjadi error internal. Silakan coba lagi atau hubungi administrator."
                )
        except Exception:
            pass  # Ignore errors when trying to send error message

def main():
    """Main function"""
    print("🚀 Starting Advanced Pterodactyl Backup Bot...")
    
    try:
        bot = AdvancedPterodactylBackupBot()
        
        # Create application
        app = Application.builder().token(bot.bot_token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", bot.start))
        app.add_handler(CommandHandler("scan", bot.scan_command))
        app.add_handler(CommandHandler("stats", bot.stats_command))
        app.add_handler(CommandHandler("clean", bot.clean_command))
        app.add_handler(CallbackQueryHandler(bot.button_handler))
        
        # Add error handler
        app.add_error_handler(bot.error_handler)
        
        print("✅ Bot started successfully!")
        print(f"📋 Loaded configuration:")
        print(f"   • Domain: {bot.domain}")
        print(f"   • Target File: {bot.target_filename}")
        print(f"   • Auto Delete: {bot.auto_delete}")
        print(f"   • Scan Subdirs: {bot.scan_subdirs}")
        print(f"   • Log Chat ID: {bot.log_chat_id or 'Not set'}")
        
        # Run bot
        print("🔄 Bot is running... Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        exit(1)

if __name__ == '__main__':
    main()