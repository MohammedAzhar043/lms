from datetime import datetime

from models.database import db


class Enrollment(db.Model):

    __tablename__ = 'enrollment'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id} {self.status}>'
