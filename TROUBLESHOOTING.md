# Bot Telegram Backup Pterodactyl - Troubleshooting Guide

## 🚨 Masalah Umum dan Solusi

### 1. Import Error / Module Not Found

**Error:** `ModuleNotFoundError: No module named 'telegram'`

**Solusi:**
```bash
# Windows
pip install python-telegram-bot==20.7 requests

# Linux/Mac
pip3 install python-telegram-bot==20.7 requests
```

### 2. Config File Error

**Error:** `File config.py tidak ditemukan!`

**Solusi:**
- Pastikan file `config.py` ada di direktori yang sama dengan `main.py`
- Jalankan `python setup.py` untuk validasi
- Edit `config.py` dengan informasi yang benar

### 3. Pterodactyl Connection Failed

**Error:** `Pterodactyl connection failed! Status: 401/403`

**Solusi:**
- Cek domain panel (harus lengkap dengan https://)
- Verifikasi Application API Key (ptla_...)
- Verifikasi Client API Key (ptlc_...)
- Pastikan API key memiliki permission yang cukup

**Cara mendapatkan API Key:**
1. Login ke panel Pterodactyl
2. Go to Account Settings > API Credentials
3. Create Application API Key dengan permission:
   - `server:list` (untuk mendapatkan daftar server)
   - `server:read` (untuk membaca info server)
4. Create Client API Key dengan permission:
   - `file:read` (untuk membaca file)
   - `file:delete` (untuk menghapus directory)

### 4. Telegram Bot Invalid

**Error:** `Invalid bot token!`

**Solusi:**
- Buat bot baru di @BotFather
- Copy token yang diberikan (format: `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ`)
- Paste ke `config.py` di `TELEGRAM_BOT_TOKEN`

### 5. Bot Tidak Menemukan File

**Error:** `No creds.json files found`

**Possible causes:**
- File tidak ada di server
- Server sedang offline
- Nama file tidak sesuai (cek `TARGET_FILENAME` di config)
- Permission API tidak cukup

**Debug steps:**
1. Login manual ke server dan cek apakah file ada
2. Cek status server di panel (harus online)
3. Test API access dengan tools seperti Postman

### 6. Backup Gagal

**Error saat send document:**

**Solusi:**
- Cek koneksi internet
- Pastikan chat log sudah di-setup (`/start` > Setup Chat Log)
- Verifikasi bot token masih valid
- Cek ukuran file (Telegram limit 50MB)

### 7. Directory Deletion Failed

**Warning:** `Backup berhasil, tapi gagal hapus direktori`

**Penyebab:**
- Permission API tidak cukup untuk delete
- Directory masih berisi file lain
- Server protection settings

**Solusi:**
- Set `AUTO_DELETE_AFTER_BACKUP = False` di config jika tidak ingin auto-delete
- Manual delete via panel setelah backup

## 🔧 Debug Mode

Untuk debugging yang lebih detail, ubah di `config.py`:

```python
LOG_LEVEL = 'DEBUG'  # Dari 'INFO' ke 'DEBUG'
LOG_TO_FILE = True   # Pastikan True untuk log ke file
```

## 📋 Checklist Troubleshooting

- [ ] Python 3.7+ terinstall
- [ ] Requirements terinstall (`pip list | grep telegram`)
- [ ] config.py ada dan valid
- [ ] Domain Pterodactyl bisa diakses
- [ ] API Keys valid dan memiliki permission
- [ ] Bot token valid dari @BotFather
- [ ] Server target online di panel
- [ ] File creds.json benar-benar ada di server
- [ ] Chat log sudah di-setup di bot

## 📞 Getting Help

1. **Check logs:** Lihat file `bot_backup.log` untuk error detail
2. **Run diagnostics:** `python setup.py` untuk test koneksi
3. **Manual test:** Test API dengan tools eksternal
4. **Clean start:** Hapus `bot_data.json` untuk reset

## 🔄 Reset Bot

Jika bot bermasalah dan perlu direset:

```bash
# Stop bot (Ctrl+C)
# Hapus data persistent
rm bot_data.json
rm bot_backup.log

# Restart bot
python main.py
```

## 🎯 Performance Tips

- Kurangi `MAX_CONCURRENT_SCANS` jika server lambat
- Increase `SCAN_TIMEOUT` untuk server yang lambat respond
- Disable `SCAN_SUBDIRECTORIES` jika tidak diperlukan untuk speed
- Set `LOG_LEVEL = 'WARNING'` untuk production (less verbose)

---

**Jika masalah persist, cek konfigurasi ulang dan pastikan semua requirements terpenuhi.**