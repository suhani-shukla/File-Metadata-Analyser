import os
import io
from flask import Blueprint, send_file, current_app, abort
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from services.metadata import get_basic_metadata
from services.hashing import calculate_hashes
from services.exif import extract_exif_metadata

download_bp = Blueprint("download", __name__)

@download_bp.route("/download/<path:filename>")
def download_pdf(filename):
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        abort(404, description="File not found")
    
    try:
        # Get metadata
        basic = get_basic_metadata(file_path, filename)
        security = calculate_hashes(file_path)
        exif, sensitive = extract_exif_metadata(file_path)
    except Exception as e:
        abort(500, description=f"Error processing file metadata: {str(e)}")
    
    # Create PDF in memory
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    y = height - 40
    
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "File Metadata Report")
    y -= 30
    
    def draw_section(title, data):
        nonlocal y
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(40, y, title)
        y -= 20
        
        pdf.setFont("Helvetica", 10)
        for key, value in data.items():
            if y < 50:
                pdf.showPage()
                y = height - 40
                pdf.setFont("Helvetica", 10)
            # Ensure value is string and handle long values
            value_str = str(value)
            if len(value_str) > 80:
                value_str = value_str[:77] + "..."
            pdf.drawString(50, y, f"{key}: {value_str}")
            y -= 14
        y -= 10
    
    draw_section("Basic Metadata", basic)
    draw_section("Hash Values", security)
    
    if exif:
        draw_section("EXIF Metadata", exif)
    
    if sensitive:
        draw_section("Sensitive Metadata Detected", {k: "⚠️" for k in sensitive})
    
    pdf.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{filename}_metadata.pdf",
        mimetype="application/pdf"
    )