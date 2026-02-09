# LearnByTech - Flask Application
# Segment 1: Project setup, config, models, DB create_all
# Segment 2: Base template, Read (list users, list courses)

from flask import Flask, render_template
from models import db, User, Course

app = Flask(__name__)

# Database configuration (use your actual password)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+mysqlconnector://lms_user1:password@localhost:3306/lms_db_1'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Bind db to this app
db.init_app(app)


@app.route('/')
def home():
    """Home page - uses base template (Segment 2)."""
    return render_template('home.html')


@app.route('/users')
def list_users():
    """Read: list all users (Segment 2)."""
    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/courses')
def list_courses():
    """Read: list all courses (Segment 2)."""
    courses = Course.query.all()
    return render_template('course_list.html', courses=courses)


# Create all tables when app runs (first time)
with app.app_context():
    db.create_all()
    print('Database tables created (user, course).')


if __name__ == '__main__':
    app.run(debug=True)
