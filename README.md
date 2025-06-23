# 🤖 Advanced Pterodactyl Backup Bot

Bot Telegram canggih untuk otomatisasi backup file `creds.json` dari server-server bot Telegram pribadi yang berjalan di panel Pterodactyl.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🎯 Fitur Utama

- **🔍 Scanning Otomatis**: Memindai semua server di panel Pterodactyl untuk mencari file `creds.json`
- **💾 Backup Aman**: Mengirim file backup ke chat Telegram pribadi yang telah ditentukan
- **🗑️ Auto Delete**: Menghapus direktori setelah backup berhasil untuk mencegah penumpukan file
- **🎮 Interactive Menu**: Menu interaktif dengan inline keyboard untuk kemudahan penggunaan
- **⚡ Sequential Scanning**: Scan server secara berurutan dengan progress tracking
- **📊 Advanced Logging**: Logging lengkap dengan multiple level dan file output
- **📈 Statistics**: Monitoring penggunaan dan statistik lengkap
- **🛡️ Error Handling**: Robust error handling dengan user-friendly messages

## 📋 Prerequisites

- **Python 3.7+**
- **Panel Pterodactyl pribadi** dengan API access
- **Bot Telegram token** (dapat diperoleh dari [@BotFather](https://t.me/BotFather))
- **Akses internet** yang stabil

## 🚀 Quick Start

### 📥 Installation

1. **Clone atau download project:**
   ```bash
   git clone <repository-url>
   cd pterodactyl-backup-bot
   ```

2. **Jalankan setup wizard:**
   ```bash
   # Windows
   python setup.py
   
   # Linux/Mac
   python3 setup.py
   ```

3. **Konfigurasi bot:**
   Edit file `config.py` dengan informasi Anda:
   ```python
   PTERODACTYL_DOMAIN = 'https://your-panel.com'
   PTERODACTYL_API_KEY = 'ptla_your_application_api_key'
   PTERODACTYL_CLIENT_API_KEY = 'ptlc_your_client_api_key'
   TELEGRAM_BOT_TOKEN = 'your_bot_token_from_botfather'
   ```

4. **Jalankan bot:**
   ```bash
   # Windows
   run.bat
   
   # Linux/Mac
   ./run.sh
   
   # Manual
   python main.py
   ```

### 🎮 Penggunaan

1. **Setup Awal:**
   - Buka chat dengan bot Anda di Telegram
   - Ketik `/start` untuk membuka menu interaktif
   - Klik "🔧 Setup Chat Log" untuk mengatur chat sebagai penerima backup

2. **Scanning File:**
   - Klik "🔍 Quick Scan" atau gunakan `/scan` untuk memindai semua server
   - Bot akan menampilkan progress scan dan daftar file yang ditemukan

3. **Backup File:**
   - Klik "🚀 Start Backup" setelah scan selesai
   - Review konfirmasi backup (⚠️ **PERINGATAN: Direktori akan dihapus!**)
   - Klik "✅ Ya, Lanjutkan" untuk memulai backup

## 📝 Perintah Available

| Perintah | Fungsi |
|----------|--------|
| `/start` | Menu utama dengan keyboard interaktif |
| `/scan` | Scan lengkap semua server dengan progress |
| `/stats` | Statistik penggunaan dan performance |
| `/clean` | Bersihkan cache scan untuk mengosongkan memory |

## ⚙️ Konfigurasi Lengkap

```python
# config.py
class Config:
    # Pterodactyl Panel
    PTERODACTYL_DOMAIN = 'https://your-panel.com'
    PTERODACTYL_API_KEY = 'ptla_your_application_api_key'
    PTERODACTYL_CLIENT_API_KEY = 'ptlc_your_client_api_key'
    
    # Server Settings
    EGGS_ID = '15'
    LOCATION_ID = '1'
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = 'your_bot_token_from_botfather'
    
    # Backup Settings
    TARGET_FILENAME = 'creds.json'
    AUTO_DELETE_AFTER_BACKUP = True  # ⚠️ HATI-HATI!
    BACKUP_FILE_PREFIX = 'creds_backup'
    
    # Scan Settings
    SCAN_SUBDIRECTORIES = True
    MAX_SCAN_DEPTH = 3
    SCAN_TIMEOUT = 30
    
    # Logging
    LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
    LOG_TO_FILE = True
    LOG_FILENAME = 'bot_backup.log'
    
    # Security
    ALLOWED_USERS = []  # Empty = allow all users
    ADMIN_USER_ID = None
    
    # Performance
    MAX_CONCURRENT_SCANS = 5
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 5
```

## 📂 Struktur Project

```
pterodactyl-backup-bot/
├── 📄 main.py                  # Bot utama
├── ⚙️ config.py                # Konfigurasi bot
├── 🔧 setup.py                 # Setup wizard
├── 📋 requirements.txt         # Dependencies
├── 🖥️ run.bat                  # Windows run script
├── 🐧 run.sh                   # Linux/Mac run script
├── 🧪 test_connectivity.py     # Test koneksi
├── 📖 README.md                # Dokumentasi
├── 🔧 TROUBLESHOOTING.md       # Panduan troubleshooting
├── 📝 CHANGELOG.md             # Riwayat perubahan
├── 🚫 .gitignore               # Git ignore rules
├── 🔐 .env.template            # Environment variables template
├── 💾 bot_data.json            # Data persistent (auto-generated)
└── 📋 bot_backup.log           # Log file (auto-generated)
```

## 🛠️ Tools & Utilities

### 🧪 Test Connectivity
```bash
python test_connectivity.py
```
Tes koneksi ke Pterodactyl dan Telegram untuk debugging.

### 🔧 Setup Wizard
```bash
python setup.py
```
Validasi instalasi, konfigurasi, dan koneksi.

### 🧹 Clean Reset
```bash
# Hapus data persistent untuk reset
rm bot_data.json bot_backup.log
```

## ⚠️ Peringatan Penting

1. **🗑️ Auto Delete**: Bot akan menghapus direktori setelah backup. Pastikan Anda sudah yakin!
2. **🔒 Private Use**: Bot ini dirancang khusus untuk panel dan server pribadi
3. **🔑 API Security**: Jangan share API key dan bot token kepada siapa pun
4. **✅ Backup Verification**: Selalu verifikasi file backup yang diterima di Telegram
5. **🧪 Testing**: Test di development server dulu sebelum production

## 🔧 Troubleshooting

### Masalah Umum

**Bot tidak bisa connect ke Pterodactyl:**
- Pastikan domain panel benar dan dapat diakses
- Cek API key Application dan Client sudah benar
- Verifikasi API key memiliki permission yang cukup

**Bot tidak menemukan file:**
- Pastikan file `creds.json` benar-benar ada di server
- Cek apakah server dalam status running
- Verifikasi `TARGET_FILENAME` di config

**Error saat backup:**
- Pastikan chat log sudah diset dengan menu Setup
- Cek koneksi internet bot
- Verifikasi bot token masih valid

**Panduan lengkap:** Lihat `TROUBLESHOOTING.md` untuk solusi detail.

## 🔒 Keamanan

- ✅ Semua API key dan token tersimpan lokal di `config.py`
- ✅ Komunikasi menggunakan HTTPS/TLS
- ✅ Bot hanya bekerja dengan server dan panel pribadi
- ✅ Optional user permission system
- ✅ Secure file handling dengan proper cleanup

## 📈 Performance

- **Sequential Scanning**: Menghindari overload server dengan scan berurutan
- **Progress Tracking**: Real-time update untuk user experience
- **Memory Efficient**: Optimized untuk handle large files
- **Error Recovery**: Automatic retry mechanism untuk network issues
- **Caching**: Smart caching untuk scan results

## 🎯 Use Cases

- **Bot Maintenance**: Backup session files sebelum server maintenance
- **Migration**: Backup files saat migrasi server
- **Disaster Recovery**: Automated backup untuk disaster recovery
- **Cleanup**: Otomatis cleanup server setelah backup
- **Monitoring**: Monitor dan backup file penting secara berkala

## 📊 Statistics & Monitoring

Bot menyediakan statistics lengkap:
- Total scans performed
- Total files backed up
- Total directories deleted
- Success/error rates
- Last operation timestamps

Access via `/stats` command untuk monitoring.

## 🔮 Future Roadmap

- [ ] **Multi-panel support** - Support multiple Pterodactyl panels
- [ ] **Scheduled backup** - Cron-like scheduling untuk backup otomatis
- [ ] **File compression** - Compress files sebelum backup
- [ ] **Cloud storage** - Integration dengan Google Drive, AWS S3
- [ ] **Web dashboard** - Web interface untuk monitoring
- [ ] **Database backup** - Support backup database files
- [ ] **Webhook notifications** - Webhook untuk external notifications
- [ ] **Multi-language** - Support multiple languages

## 📄 License

Project ini menggunakan MIT License. Lihat file `LICENSE` untuk detail.

## 🤝 Contributing

Contributions welcome! Silakan:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

Jika mengalami masalah:
1. **Check logs**: Lihat `bot_backup.log` untuk error detail
2. **Run diagnostics**: `python setup.py` untuk test koneksi
3. **Test connectivity**: `python test_connectivity.py`
4. **Read troubleshooting**: Lihat `TROUBLESHOOTING.md`
5. **Clean reset**: Hapus `bot_data.json` untuk reset

## ⭐ Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [Pterodactyl Panel](https://pterodactyl.io/) - Game server management panel
- [Requests](https://requests.readthedocs.io/) - HTTP library untuk Python

---

**⚠️ Disclaimer**: Bot ini dibuat untuk kepentingan backup dan maintenance server pribadi. Gunakan dengan bijaksana dan bertanggung jawab. Selalu backup data penting sebelum menjalankan operasi yang destructive.

**🎉 Happy Backing Up!** 🎉