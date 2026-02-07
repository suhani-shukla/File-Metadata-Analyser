from flask import Blueprint, render_template, request, current_app
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from models import db, File

upload_bp = Blueprint("upload", __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route("/")
def index():
    return render_template("index.html")

@upload_bp.route("/upload", methods=["POST"])
def upload():
    # Check if file is in request
    if 'file' not in request.files:
        return "No file part in request", 400
    
    file = request.files["file"]
    
    # Check if filename is empty
    if file.filename == "":
        return "No file selected", 400
    
    # Validate file extension
    if not allowed_file(file.filename):
        return f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}", 400
    
    # Sanitize filename to prevent path traversal attacks
    original_filename = secure_filename(file.filename)
    
    # Handle duplicate filenames by appending timestamp
    base_name, extension = os.path.splitext(original_filename)
    filename = original_filename
    counter = 1
    
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    
    # Check if file already exists and create unique name
    while os.path.exists(file_path):
        filename = f"{base_name}_{counter}{extension}"
        file_path = os.path.join(upload_folder, filename)
        counter += 1
    
    # Save file
    try:
        file.save(file_path)
    except Exception as e:
        return f"Error saving file: {str(e)}", 500
    
    # Check file size after saving
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)  # Delete the file
        return f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB", 400
    
    # Save to database
    try:
        new_file = File(
            filename=filename,
            filesize=file_size,
            filetype=file.content_type,
            upload_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        db.session.add(new_file)
        db.session.commit()
    except Exception as e:
        # If database save fails, remove the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        return f"Database error: {str(e)}", 500
    
    return render_template("index.html", filename=filename)