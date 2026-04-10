from datetime import datetime

from models.database import db


class Course(db.Model):
    """Course table: one course belongs to one teacher."""
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft / published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher = db.relationship('User', backref='courses')

    def __repr__(self):
        return f'<Course {self.title}>'
