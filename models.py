# models.py
from flask_login import UserMixin
from extensions import db  # Import db from extensions

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)

class CVAnalysis(db.Model):
    __tablename__ = 'cv_analysis'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(150), nullable=False)
    context_score = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=True)
    designation = db.Column(db.String(150), nullable=True)
    experience = db.Column(db.String(150), nullable=True)
    education = db.Column(db.String(150), nullable=True)
    skills = db.Column(db.String(150), nullable=True)
