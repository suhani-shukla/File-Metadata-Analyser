from flask import Blueprint, render_template, current_app, abort
import os
from models import db, File, Metadata, VTDetection
from services.hashing import calculate_hashes
from services.exif import extract_exif_metadata
from services.virustotal import scan_file, get_analysis, get_report_by_hash

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
                    value=str(value),
                    is_sensitive=(key in sensitive)
                )
                db.session.add(entry)
            db.session.commit()

        # VirusTotal scan — run once, cache results in DB
        vt_result = None
        vt_error = None

        if file.vt_verdict is None:
            # First try by hash (faster, doesn't consume upload quota)
            vt_result = get_report_by_hash(file.sha256) if file.sha256 else None

            # If not found by hash, upload the file for a fresh scan
            if vt_result is None:
                scan = scan_file(file_path)
                if "error" in scan:
                    vt_error = scan["error"]
                else:
                    analysis = get_analysis(scan["analysis_id"])
                    if "error" in analysis:
                        vt_error = analysis["error"]
                        # Store analysis_id so user can retry later
                        file.vt_analysis_id = scan["analysis_id"]
                    else:
                        vt_result = analysis

            # Persist result to DB
            if vt_result:
                file.vt_verdict = vt_result["verdict"]
                file.vt_malicious = vt_result["malicious"]
                file.vt_suspicious = vt_result["suspicious"]
                file.vt_undetected = vt_result["undetected"]
                file.vt_total = vt_result["total"]

                for det in vt_result.get("detections", []):
                    db.session.add(VTDetection(
                        file_id=file.id,
                        engine=det["engine"],
                        category=det["category"],
                        result=det["result"],
                    ))
                db.session.commit()

        else:
            # Already scanned — load from DB
            vt_result = {
                "verdict": file.vt_verdict,
                "malicious": file.vt_malicious,
                "suspicious": file.vt_suspicious,
                "undetected": file.vt_undetected,
                "total": file.vt_total,
                "detections": [
                    {"engine": d.engine, "category": d.category, "result": d.result}
                    for d in file.vt_detections
                ],
            }

    except Exception as e:
        print(f"Error processing file metadata: {str(e)}")
        vt_error = "An unexpected error occurred during scanning."
        vt_result = None

    # Gather metadata for template
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
        sensitive=sensitive_fields,
        vt=vt_result,
        vt_error=vt_error,
    )