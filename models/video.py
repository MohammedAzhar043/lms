from datetime import datetime

from models.database import db


class Video(db.Model):

    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship('Course', backref='videos')

    def __repr__(self):
        return f'<Video {self.title}>'
