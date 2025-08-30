from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables FIRST
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
   
    # Get database credentials - FIXED: Use correct environment variable names
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = os.getenv('MYSQL_PORT', '3306')
    database = os.getenv('MYSQL_DATABASE')
   
    # Debug: Print to verify credentials are loaded
    print(f"Database config: {user}@{host}:{port}/{database}")
   
    if not all([user, password, host, database]):
        missing_vars = []
        if not user: missing_vars.append('MYSQL_USER')
        if not password: missing_vars.append('MYSQL_PASSWORD')
        if not host: missing_vars.append('MYSQL_HOST')
        if not database: missing_vars.append('MYSQL_DATABASE')
        raise ValueError(f"Missing required database environment variables: {', '.join(missing_vars)}")
   
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # FIXED: Use dynamic database URI construction
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
   
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
   
    # Register blueprints
    from routes import main
    app.register_blueprint(main, url_prefix='/api')
   
    return app