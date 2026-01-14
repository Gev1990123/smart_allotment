import os
import shutil
from datetime import datetime

# Paths relative to project root
# Calculate project root
current_dir = os.path.abspath(os.path.dirname(__file__))
while os.path.basename(current_dir) != 'smart_allotment':
    parent = os.path.dirname(current_dir)
    if parent == current_dir:
        raise RuntimeError("Could not find smart_allotment project root")
    current_dir = parent

PROJECT_ROOT = current_dir
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