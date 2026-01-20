# Exit on any error
set -e

echo "=== Smart Allotment FULL PRODUCTION Setup ==="

WORKING_DIR=$(pwd)
USER=$(whoami)
SERVICE_NAME="smart-allotment"  # Your service name

# System setup (Raspberry Pi)
if [ -f /proc/device-tree/model ] && grep -q "Raspberry" /proc/device-tree/model; then
    echo "Raspberry Pi PRODUCTION"
    sudo apt-get update && sudo apt-get upgrade -y -qq
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip \
        postgresql postgresql-contrib libpq-dev i2c-tools libi2c-dev build-essential \
        nginx supervisor git
    sudo raspi-config nonint do_i2c 0
else
    echo "Non-RPi PRODUCTION"
    sudo apt-get update && sudo apt-get install -y postgresql libpq-dev build-essential nginx supervisor git
fi

# PostgreSQL setup
echo "PostgreSQL setup..."
sudo systemctl restart postgresql && sudo systemctl enable postgresql
sudo -u postgres psql -c "CREATE USER IF NOT EXISTS smartallotment WITH PASSWORD 'smartallotment' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE smart_allotment OWNER smartallotment;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE smart_allotment TO smartallotment;"

# Python venv + dependencies
echo "Python 3.11 venv..."
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel gunicorn
pip install RPi.GPIO==0.7.1 smbus2==0.4.1 adafruit-circuitpython-ads1x15 adafruit_ads1x15 adafruit-circuitpython-bh1750 flask==2.3.2 flask-wtf==1.2.1 flask-limiter==3.5.0 gunicorn flask-sqlalchemy==3.0.5 psycopg2-binary requests==2.32.0 paho-mqtt==1.6.1 python-dotenv==1.0.0 psutil

# Production .env
cat > .env << EOF
DATABASE_URL=postgresql://smartallotment:smartallotment@localhost/smart_allotment
SQLALCHEMY_DATABASE_URI=postgresql://smartallotment:smartallotment@localhost/smart_allotment
SQLALCHEMY_TRACK_MODIFICATIONS=False
SECRET_KEY=prod-$(date +%s)-change-me
WTF_CSRF_ENABLED=True
DEBUG=False
ENVIRONMENT=production
MQTT_BROKER=localhost
MQTT_PORT=1883
EOF

# Create database tables
echo "Database tables..."
python3 << EOF
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
os.environ['ENVIRONMENT'] = 'production'
from app import create_app
app = create_app()
with app.app_context():
    from app.extensions import db
    db.create_all()
print("Tables created!")
EOF

# Ensure deploy.sh is executable (already in repo)
chmod +x deploy.sh

# 1. MAIN APP SERVICE (matches your service name)
sudo tee /etc/systemd/system/smart-allotment.service > /dev/null << EOF
[Unit]
Description=Smart Allotment Production App
After=network.target postgresql.service

[Service]
Type=notify
User=$USER
WorkingDirectory=$WORKING_DIR
Environment=PATH=$WORKING_DIR/venv/bin
ExecStart=$WORKING_DIR/venv/bin/gunicorn 'app:create_app()':app --bind 127.0.0.1:5000 --workers 3 --worker-class gevent --timeout 120
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 2. GIT UPDATE SERVICE (uses YOUR deploy.sh)
sudo tee /etc/systemd/system/smart_allotment_update.service > /dev/null << EOF
[Unit]
Description=Smart Allotment Git Auto Update
Type=oneshot
User=$USER
WorkingDirectory=$WORKING_DIR
ExecStart=$WORKING_DIR/deploy.sh
EOF

# 3. YOUR EXACT TIMER (5min checks, 2min after boot)
sudo tee /etc/systemd/system/smart_allotment_update.timer > /dev/null << EOF
[Unit]
Description=Check GitHub for updates every 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable smart-allotment
sudo systemctl enable smart_allotment_update.timer
sudo systemctl start smart-allotment
sudo systemctl start smart_allotment_update.timer

echo "FULL PRODUCTION SETUP COMPLETE!"
echo ""
echo "Services:"
echo "• Main app:        sudo systemctl status smart-allotment"
echo "• Git updates:     sudo systemctl status smart_allotment_update.timer" 
echo "• Deploy logs:     $WORKING_DIR/logs/deploy.log"
echo ""
echo "Timer: Every 5 minutes → YOUR deploy.sh → smart-allotment restart"
echo "Dashboard: http://localhost:5000"
echo "Database: smart_allotment DB ready"
echo ""
echo "SECURITY: Change DB password in .env"