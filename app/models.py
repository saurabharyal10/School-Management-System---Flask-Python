from app import db
from flask_login import UserMixin
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # <== ADD THIS
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    profile_image = db.Column(db.String(100), nullable=True)
    qualification = db.Column(db.String(50), nullable=False)
    other_qualification = db.Column(db.String(100))
    document_type = db.Column(db.String(50), nullable=False)
    other_document = db.Column(db.String(100))
    document_filename = db.Column(db.String(150), nullable=True)  # change from False to True
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    password_hash = db.Column(db.String(128), nullable=False)  # <== UNCOMMENT
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ContactMessage(db.Model):
    __tablename__ = 'tbl_contact_us'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
