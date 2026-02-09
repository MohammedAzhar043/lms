# LearnByTech - Flask Application
# Segment 1: Project setup, config, models, DB create_all

from flask import Flask
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
    """Simple route to verify app runs - Segment 1."""
    return 'LearnByTech - Project is running!'


# Create all tables when app runs (first time)
with app.app_context():
    db.create_all()
    print('Database tables created (user, course).')


if __name__ == '__main__':
    app.run(debug=True)
