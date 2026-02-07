import os

# Database configuration with environment variable support
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Upload folder configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

# Security configuration
SECRET_KEY = os.environ.get('SECRET_KEY')
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size