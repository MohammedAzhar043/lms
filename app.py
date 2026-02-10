# LearnByTech - Flask Application
# Segment 1: Project setup, config, models, DB create_all
# Segment 2: Base template, Read (list users, list courses)
# Segment 3: User Create (registration form + route)
# Segment 4: User Read (list + detail)
# Segment 5: User Update (edit form + route)
# Segment 6: User Delete
# Segment 7: Course Create
# Segment 8: Course Read (list + detail)
# Segment 9: Course Update and Delete

from flask import Flask, render_template, request, redirect, url_for
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Create: user registration (Segment 3). GET = form, POST = save and redirect."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('list_users'))
    return render_template('register.html')


@app.route('/user/<int:id>')
def user_detail(id):
    """Read: single user detail (Segment 4)."""
    user = User.query.get_or_404(id)
    return render_template('user_detail.html', user=user)


@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    """Update: edit user (Segment 5). GET = form with data, POST = save and redirect."""
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.password = request.form['password']
        user.role = request.form['role']
        db.session.commit()
        return redirect(url_for('list_users'))
    return render_template('user_edit.html', user=user)


@app.route('/user/delete/<int:id>')
def delete_user(id):
    """Delete: remove user (Segment 6). Redirect to list after delete."""
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))


@app.route('/course/create', methods=['GET', 'POST'])
def course_create():
    """Create: add course (Segment 7). GET = form, POST = save and redirect."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        teacher_id = request.form['teacher_id']
        course = Course(title=title, description=description, teacher_id=int(teacher_id))
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('list_courses'))
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('course_form.html', teachers=teachers)


@app.route('/course/<int:id>')
def course_detail(id):
    """Read: single course detail (Segment 8)."""
    course = Course.query.get_or_404(id)
    return render_template('course_detail.html', course=course)


@app.route('/course/edit/<int:id>', methods=['GET', 'POST'])
def course_edit(id):
    """Update: edit course (Segment 9). GET = form with data, POST = save and redirect."""
    course = Course.query.get_or_404(id)
    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form.get('description', '')
        course.teacher_id = int(request.form['teacher_id'])
        db.session.commit()
        return redirect(url_for('list_courses'))
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('course_edit.html', course=course, teachers=teachers)


@app.route('/course/delete/<int:id>')
def course_delete(id):
    """Delete: remove course (Segment 9). Redirect to list after delete."""
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('list_courses'))


# Create all tables when app runs (first time)
with app.app_context():
    db.create_all()
    print('Database tables created (user, course).')


if __name__ == '__main__':
    app.run(debug=True)
