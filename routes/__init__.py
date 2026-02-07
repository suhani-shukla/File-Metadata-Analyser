from .download import download_bp
from .upload import upload_bp
from .details import details_bp

def register_routes(app):
    app.register_blueprint(upload_bp)
    app.register_blueprint(details_bp)
    app.register_blueprint(download_bp)