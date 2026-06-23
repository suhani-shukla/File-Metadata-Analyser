import os
import time
import requests

VIRUSTOTAL_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY")
VT_BASE = "https://www.virustotal.com/api/v3"

HEADERS = {
    "x-apikey": VIRUSTOTAL_API_KEY or "",
    "Accept": "application/json",
}


def scan_file(file_path: str) -> dict:
    """
    Upload a file to VirusTotal for scanning.
    Returns the analysis ID.
    """
    if not VIRUSTOTAL_API_KEY:
        return {"error": "VirusTotal API key not configured."}

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{VT_BASE}/files",
                headers={"x-apikey": VIRUSTOTAL_API_KEY},
                files={"file": (os.path.basename(file_path), f)},
                timeout=30,
            )
        response.raise_for_status()
        data = response.json()
        return {"analysis_id": data["data"]["id"]}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_analysis(analysis_id: str, retries: int = 5, delay: int = 15) -> dict:
    """
    Poll VirusTotal for analysis results until completed.
    Returns the parsed result dict or an error.
    """
    if not VIRUSTOTAL_API_KEY:
        return {"error": "VirusTotal API key not configured."}

    for attempt in range(retries):
        try:
            response = requests.get(
                f"{VT_BASE}/analyses/{analysis_id}",
                headers=HEADERS,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            status = data["data"]["attributes"]["status"]

            if status == "completed":
                return parse_analysis(data)

            # Not ready yet — wait and retry
            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    return {"error": "Analysis timed out. Try refreshing the page in a minute."}


def get_report_by_hash(sha256: str) -> dict:
    """
    Fetch a VirusTotal report by SHA-256 hash (faster than uploading if already known).
    Returns parsed result or None if not found.
    """
    if not VIRUSTOTAL_API_KEY:
        return None

    try:
        response = requests.get(
            f"{VT_BASE}/files/{sha256}",
            headers=HEADERS,
            timeout=15,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        # Hash report has same structure under data.attributes.last_analysis_stats
        return parse_file_report(data)
    except requests.exceptions.RequestException:
        return None


def parse_analysis(data: dict) -> dict:
    """Parse a /analyses response into a clean result dict."""
    attrs = data["data"]["attributes"]
    stats = attrs.get("stats", {})
    results = attrs.get("results", {})
    return _build_result(stats, results)


def parse_file_report(data: dict) -> dict:
    """Parse a /files/{hash} response into a clean result dict."""
    attrs = data["data"]["attributes"]
    stats = attrs.get("last_analysis_stats", {})
    results = attrs.get("last_analysis_results", {})
    return _build_result(stats, results)


def _build_result(stats: dict, results: dict) -> dict:
    """Shared builder for both analysis and file-report responses."""
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    undetected = stats.get("undetected", 0)
    total = malicious + suspicious + undetected + stats.get("harmless", 0)

    # Determine overall verdict
    if malicious >= 3:
        verdict = "malicious"
    elif malicious >= 1 or suspicious >= 2:
        verdict = "suspicious"
    else:
        verdict = "clean"

    # Build per-engine breakdown (only flagging engines)
    detections = []
    for engine, info in results.items():
        if isinstance(info, dict) and info.get("category") in ("malicious", "suspicious"):
            detections.append({
                "engine": engine,
                "category": info.get("category"),
                "result": info.get("result") or "—",
            })

    return {
        "verdict": verdict,
        "malicious": malicious,
        "suspicious": suspicious,
        "undetected": undetected,
        "total": total,
        "detections": detections,
    }