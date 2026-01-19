from app import create_app
from app.config import DevConfig, ProdConfig

app = create_app(ProdConfig if os.getenv('FLASK_ENV') == 'production' else DevConfig)

if __name__ == '__main__':
    app.run()