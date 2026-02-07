from flask import Blueprint, render_template, current_app, abort
import os
from models import db, File, Metadata
from services.hashing import calculate_hashes
from services.exif import extract_exif_metadata

details_bp = Blueprint("details", __name__)

@details_bp.route("/details/<path:filename>")
def details(filename):
    # Query database for file
    file = File.query.filter_by(filename=filename).first()
    if not file:
        abort(404, description="File not found in database")
    
    # Use config for upload folder
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    
    # Check if physical file exists
    if not os.path.exists(file_path):
        abort(404, description="Physical file not found. It may have been deleted.")
    
    try:
        # Calculate hashes once
        if not file.md5 or not file.sha256:
            hashes = calculate_hashes(file_path)
            file.md5 = hashes["md5"]
            file.sha256 = hashes["sha256"]
            db.session.commit()
        
        # Store EXIF metadata once
        if not file.metadata_entries:
            exif, sensitive = extract_exif_metadata(file_path)
            for key, value in exif.items():
                entry = Metadata(
                    file_id=file.id,
                    key=key,
                    value=str(value),  # Ensure value is string
                    is_sensitive=(key in sensitive)
                )
                db.session.add(entry)
            db.session.commit()
    except Exception as e:
        # Log error and continue with partial data
        print(f"Error processing file metadata: {str(e)}")
    
    # Gather metadata
    exif_data = {m.key: m.value for m in file.metadata_entries}
    sensitive_fields = [m.key for m in file.metadata_entries if m.is_sensitive]
    
    basic = {
        "filename": file.filename,
        "filesize": file.filesize,
        "filetype": file.filetype,
        "upload_time": file.upload_time
    }
    
    security = {
        "md5": file.md5 or "Not calculated",
        "sha256": file.sha256 or "Not calculated"
    }
    
    return render_template(
        "details.html",
        basic=basic,
        security=security,
        exif=exif_data,
        sensitive=sensitive_fields
    )