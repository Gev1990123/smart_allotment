import os
import shutil
from datetime import datetime

# Paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'smart_allotment.db')
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'data', 'backups')

os.makedirs(BACKUP_DIR, exist_ok=True)

# Create timestamped backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(BACKUP_DIR, f"smart_allotment_{timestamp}.db")

# Simple file copy (safe while service runs)
shutil.copy2(DB_PATH, backup_file)
print(f"✅ Backup created: {backup_file}")
print(f"📁 Location: {BACKUP_DIR}")