from datetime import datetime

from models.database import db


class MCQ(db.Model):

    __tablename__ = 'mcq'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.String(10), nullable=False)
    marks = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    course = db.relationship('Course', backref='mcqs')

    def __repr__(self):
        return f'<MCQ {self.question_text[:50]}>'


class MCQAttempt(db.Model):

    __tablename__ = 'mcq_attempt'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mcq_id = db.Column(db.Integer, db.ForeignKey('mcq.id'), nullable=False)
    selected_answer = db.Column(db.String(10), nullable=False)
    score = db.Column(db.Integer, default=0)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='mcq_attempt')
    mcq = db.relationship('MCQ', backref='attempts')

    def __repr__(self):
        return f'<MCQAttempt user= {self.user_id} mcq={self.mcq_id} score = {self.score}>'
