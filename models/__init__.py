
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# db instance will be set by app.py
db = SQLAlchemy()


class User(db.Model):
    """User table: students and teachers. Role stored here ."""
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


class Enrollment(db.Model):

    __tablename__ = 'enrollment'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    course_id  = db.Column(db.Integer,db.ForeignKey('course.id'),nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    user = db.relationship('User',backref='enrollments')
    course = db.relationship('Course',backref='enrollments')

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id} {self.status}>'



class Video(db.Model):

    __tablename__ = 'video'

    id = db.Column(db.Integer,primary_key=True)
    course_id=db.Column(db.Integer,db.ForeignKey('course.id'),nullable=False)
    title =  db.Column(db.String(200),nullable=False)
    file_path = db.Column(db.String(500),nullable=False)
    order = db.Column(db.Integer,default=0)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    course = db.relationship('Course',backref='videos')

    def __repr__(self):
        return f'<Video {self.title}>'


class Note(db.Model):

    __tablename__= 'note'

    id = db.Column(db.Integer,primary_key=True)
    course_id = db.Column(db.Integer,db.ForeignKey('course.id'),nullable=False)
    title = db.Column(db.String(200),nullable=False)
    file_path = db.Column(db.String(500),nullable=False)
    order = db.Column(db.Integer,default=0)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

    course = db.relationship('Course',backref='notes')


    def __repr__(self):
        return f'<Note {self.title}>'



class MCQ(db.Model):

    __tablename__= 'mcq'


    id = db.Column(db.Integer,primary_key=True)
    course_id= db.Column(db.Integer,db.ForeignKey('course.id'),nullable=False)
    question_text = db.Column(db.Text,nullable=False)
    option_a = db.Column(db.String(500),nullable=False)
    option_b = db.Column(db.String(500),nullable=False)
    option_c = db.Column(db.String(500),nullable=False)
    option_d = db.Column(db.String(500),nullable=False)
    correct_answer = db.Column(db.String(10),nullable=False)
    marks = db.Column(db.Integer,default=1)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)


    course = db.relationship('Course',backref='mcqs')

    def __repr__(self):
        return f'<MCQ {self.question_text[:50]}>'


class MCQAttempt(db.Model):

    __tablename__ = 'mcq_attempt'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    mcq_id = db.Column(db.Integer,db.ForeignKey('mcq.id'),nullable=False)
    selected_answer = db.Column(db.String(10),nullable=False)
    score = db.Column(db.Integer,default=0)
    attempted_at = db.Column(db.DateTime,default=datetime.utcnow)

    user = db.relationship('User',backref='mcq_attempt')
    mcq = db.relationship('MCQ',backref='attempts')


    def __repr__(self):
        return f'<MCQAttempt user= {self.user_id} mcq={self.mcq_id} score = {self.score}>'

