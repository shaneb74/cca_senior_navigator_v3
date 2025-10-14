# How to Clear Session & User Data

## Quick Commands

### 🧹 Clear Everything (Nuclear Option)
```bash
python clear_data.py --clear-all
```
Deletes **all** sessions and users. Use when you want a completely fresh start.

### 📝 Clear Sessions Only (Keep User Data)
```bash
python clear_data.py --clear-sessions
```
Deletes browser session files but keeps user profiles/progress.

### 👤 Clear Specific User
```bash
# First, list users to get their UID
python clear_data.py --list

# Then delete specific user
python clear_data.py --clear-user anon_abc123def456
```

### 🗑️ Cleanup Old Sessions (7+ Days)
```bash
python clear_data.py --cleanup
```
Removes stale sessions automatically (same as the app's auto-cleanup).

---

## Inspection Commands

### 📋 List All Files
```bash
python clear_data.py --list
```
Shows all sessions and users with:
- Session ID / User ID
- Created/accessed timestamps
- Current route / Profile name
- File sizes

Example output:
```
=== SESSION FILES ===

📄 session_abc123.json
   ID: abc-123-def-456
   Created: 2025-10-14 10:23:45
   Last Accessed: 2025-10-14 11:30:12
   Route: gcp_v4
   Size: 2,453 bytes

=== USER FILES ===

👤 anon_a1b2c3d4.json
   UID: anon_a1b2c3d4
   Name: No name
   Created: 2025-10-14 10:23:45
   Last Updated: 2025-10-14 11:30:12
   Completed Products: 1
   Size: 8,742 bytes
```

### 📊 Show Storage Stats
```bash
python clear_data.py --stats
```
Shows:
- Session count and total size
- User count and total size
- Combined storage usage

Example output:
```
=== STORAGE STATISTICS ===

📊 Sessions:
   Count: 3
   Total Size: 7,359 bytes (7.2 KB)
   Avg Size: 2,453 bytes

👥 Users:
   Count: 2
   Total Size: 17,484 bytes (17.1 KB)
   Avg Size: 8,742 bytes

💾 Total:
   Combined Size: 24,843 bytes (24.3 KB)
```

### 🔍 Inspect Specific File
```bash
python clear_data.py --inspect .cache/session_abc123.json
```
Shows the raw JSON contents of a file.

---

## Manual Deletion (Without Script)

### Delete All Data
```bash
rm -rf .cache/ data/users/
```

### Delete Sessions Only
```bash
rm -rf .cache/
```

### Delete Specific User
```bash
rm data/users/anon_abc123def456.json
```

### Delete Old Sessions (8+ days)
```bash
find .cache/ -name "session_*.json" -mtime +7 -delete
```

---

## Common Scenarios

### 🔄 "I want to test from scratch"
```bash
python clear_data.py --clear-all
streamlit run app.py
```

### 🧪 "I want to test session persistence"
```bash
# Start GCP, answer some questions, then...
python clear_data.py --clear-sessions
# Refresh browser - should start fresh (user data still there)
```

### 🐛 "I corrupted my data testing"
```bash
python clear_data.py --clear-all
# Fresh start with no corrupted files
```

### 📈 "I want to see what's being saved"
```bash
python clear_data.py --list
python clear_data.py --inspect data/users/anon_*.json
```

### 🧹 "I want to clean up old test data"
```bash
python clear_data.py --cleanup 1  # Remove sessions older than 1 day
```

---

## Safety Features

- **Confirmation prompts** for destructive operations
- **--clear-all** requires typing 'y' to confirm
- **--list** first to see what will be deleted
- **File backups** (manual): `cp -r .cache/ .cache.backup/`

---

## Help
```bash
python clear_data.py --help
```

Shows all available commands and examples.
