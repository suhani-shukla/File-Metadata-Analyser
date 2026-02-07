from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from config import *
from models import db
from routes import register_routes

# ------------------------
# CREATE FLASK APP
# ------------------------
app = Flask(__name__)
app.config.from_object("config")

# ------------------------
# INIT DATABASE (PostgreSQL)
# ------------------------
db.init_app(app)

# ------------------------
# REGISTER ALL ROUTES
# ------------------------
register_routes(app)

# ------------------------
# RUN SERVER
# ------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
