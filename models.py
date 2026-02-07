from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    filesize = db.Column(db.Integer)
    filetype = db.Column(db.String(100))
    upload_time = db.Column(db.String(50))
    md5 = db.Column(db.String(64))
    sha256 = db.Column(db.String(64))

    metadata_entries = db.relationship(
        "Metadata", backref="file", cascade="all, delete"
    )


class Metadata(db.Model):
    __tablename__ = "metadata"

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("files.id"))
    key = db.Column(db.String(255))
    value = db.Column(db.Text)
    is_sensitive = db.Column(db.Boolean)
