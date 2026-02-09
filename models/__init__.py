# LearnByTech - Models
# User and Course models for Segment 1

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# db instance will be set by app.py
db = SQLAlchemy()


class User(db.Model):
    """User table: students and teachers. Role stored here (no admin)."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Course(db.Model):
    """Course table: one course belongs to one teacher."""
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft / published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: course belongs to one teacher (User with role=teacher)
    teacher = db.relationship('User', backref='courses')

    def __repr__(self):
        return f'<Course {self.title}>'
