import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from .extensions import db, csrf
from .config import DevConfig

def create_app(config_class=DevConfig):
    # Load .env first
    load_dotenv()
    
    # Create app
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.template_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dashboard', 'templates')
    app.static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dashboard', 'static') 

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from .routes.main import main_bp
    from .routes.probes import probes_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(probes_bp)
    
    # Initialize sensors ONCE at startup
    with app.app_context():
        #db.create_all()
        from sensors.soil_moisture import soil_init_channels
        from sensors.light import light_init_channels
        from sensors.temperature import temp_init_channels
        
        soil_init_channels()
        light_init_channels()
        temp_init_channels()
    
    # Start sensor background task
    from .tasks.sensor_loop import start_sensor_loop
    start_sensor_loop(app)
    
    return app