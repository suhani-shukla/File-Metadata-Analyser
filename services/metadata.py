import os
import mimetypes
from datetime import datetime

def get_basic_metadata(file_path, filename):
    return {
        "filename": filename,
        "filesize": os.path.getsize(file_path),
        "filetype": mimetypes.guess_type(file_path)[0],
        "upload_time": datetime.fromtimestamp(
            os.path.getmtime(file_path)
        ).strftime("%Y-%m-%d %H:%M:%S")
    }
