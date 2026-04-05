# 📁 File Metadata Analyser

A secure Flask-based web application that analyzes uploaded files by extracting metadata, generating cryptographic hashes, and performing threat intelligence checks using the VirusTotal API.

---

## 🚀 Features

* 🔍 **Metadata Extraction** – Extracts detailed file metadata (size, type, timestamps, etc.)
* 🔐 **Hash Generation** – Generates MD5 and SHA-256 hashes for file fingerprinting
* 🛡️ **Threat Intelligence Integration** – Uses VirusTotal API (v3) to scan files across multiple antivirus engines
* ⚠️ **Risk Classification** – Categorizes files as *Safe*, *Suspicious*, or *Malicious*
* 🧠 **Custom Risk Logic** – Implements intelligent evaluation based on detection results
* 🗄️ **Database Storage** – Stores file data, hashes, metadata, and analysis results in PostgreSQL

---

## 🏗️ Tech Stack

* **Backend:** Flask (Python)
* **Database:** PostgreSQL
* **APIs:** VirusTotal API v3
* **Security:** Hashing (MD5, SHA-256)

---

## 📂 Project Structure

```
file-metadata-analyser/
│
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── models/                 # Database models
├── routes/                 # Application routes
├── utils/                  # Utility functions (hashing, metadata extraction)
├── templates/              # HTML templates
├── static/                 # CSS, JS, assets
├── uploads/                # Uploaded files (if stored locally)
├── requirements.txt        # Python dependencies
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-link>
cd file-metadata-analyser
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

* Create a PostgreSQL database
* Update connection string in `config.py`

Example:

```python
SQLALCHEMY_DATABASE_URI = "postgresql://username:password@localhost/db_name"
```

### 5. Configure Environment Variables

Create a `.env` file and add:

```
VIRUSTOTAL_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key
```

---

## ▶️ Running the Application

```bash
flask run
```

Then open:

```
http://127.0.0.1:5000
```

---

## 🔄 Workflow

1. User uploads a file
2. System extracts metadata
3. Generates MD5 & SHA-256 hashes
4. Sends hash/file to VirusTotal API
5. Receives scan results from multiple engines
6. Applies custom risk evaluation logic
7. Stores results in PostgreSQL database
8. Displays analysis to user

---

## 🧪 Example Output

| File Name  | MD5 Hash  | SHA-256   | Status    |
| ---------- | --------- | --------- | --------- |
| sample.exe | abc123... | def456... | Malicious |

---

## 🔐 Security Considerations

* File size limits enforced
* Secure file upload handling
* API key stored in environment variables
* Hash-based scanning avoids unnecessary file uploads

---

## 📌 Future Enhancements

* 📊 Dashboard with analytics
* 📁 Bulk file upload support
* 🤖 Machine learning-based threat detection
* 🔔 Email alerts for malicious files
* 🌐 REST API endpoints

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙌 Acknowledgements

* VirusTotal for threat intelligence API
* Flask community for lightweight web framework

---

## 📬 Contact

For any queries or suggestions, feel free to reach out.
