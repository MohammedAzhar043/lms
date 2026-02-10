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

from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Course

app = Flask(__name__)

# Secret key required for session (used by flash messages)
app.config['SECRET_KEY'] = 'learnbytech-secret-key-change-in-production'

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
    """Create: user registration (Segment 3). Validation + Flash (Segment 1 & 2)."""
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip()
        password = (request.form.get('password') or '')
        role = request.form.get('role', '').strip()

        # Backend validation (Segment 1 & 2)
        if not username:
            flash('Username is required.', 'error')
            return render_template('register.html', username=username, email=email, role=role)
        if not email:
            flash('Email is required.', 'error')
            return render_template('register.html', username=username, email=email, role=role)
        if '@' not in email:
            flash('Enter a valid email address.', 'error')
            return render_template('register.html', username=username, email=email, role=role)
        if not password:
            flash('Password is required.', 'error')
            return render_template('register.html', username=username, email=email, role=role)
        if len(password) < 4:
            flash('Password must be at least 4 characters.', 'error')
            return render_template('register.html', username=username, email=email, role=role)
        if role not in ('student', 'teacher'):
            flash('Please select a valid role.', 'error')
            return render_template('register.html', username=username, email=email, role=role)

        # Unique username and email (Segment 2)
        if User.query.filter_by(username=username).first():
            flash('This username is already taken.', 'error')
            return render_template('register.html', username=username, email=email, role=role)
        if User.query.filter_by(email=email).first():
            flash('This email is already registered.', 'error')
            return render_template('register.html', username=username, email=email, role=role)

        try:
            user = User(username=username, email=email, password=password, role=role)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful.', 'success')
            return redirect(url_for('list_users'))
        except Exception:
            db.session.rollback()
            flash('Something went wrong. Please try again.', 'error')
            return render_template('register.html', username=username, email=email, role=role)
    return render_template('register.html')


@app.route('/user/<int:id>')
def user_detail(id):
    """Read: single user detail (Segment 4)."""
    user = User.query.get_or_404(id)
    return render_template('user_detail.html', user=user)


@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    """Update: edit user (Segment 5). Validation + Flash (Segment 3)."""
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip()
        password = (request.form.get('password') or '')
        role = request.form.get('role', '').strip()

        # Backend validation (Segment 3)
        if not username:
            flash('Username is required.', 'error')
            return render_template('user_edit.html', user=user)
        if not email:
            flash('Email is required.', 'error')
            return render_template('user_edit.html', user=user)
        if '@' not in email:
            flash('Enter a valid email address.', 'error')
            return render_template('user_edit.html', user=user)
        if not password:
            flash('Password is required.', 'error')
            return render_template('user_edit.html', user=user)
        if len(password) < 4:
            flash('Password must be at least 4 characters.', 'error')
            return render_template('user_edit.html', user=user)
        if role not in ('student', 'teacher'):
            flash('Please select a valid role.', 'error')
            return render_template('user_edit.html', user=user)

        # Unique username/email (exclude current user)
        other = User.query.filter_by(username=username).first()
        if other and other.id != user.id:
            flash('This username is already taken.', 'error')
            return render_template('user_edit.html', user=user)
        other = User.query.filter_by(email=email).first()
        if other and other.id != user.id:
            flash('This email is already registered.', 'error')
            return render_template('user_edit.html', user=user)

        try:
            user.username = username
            user.email = email
            user.password = password
            user.role = role
            db.session.commit()
            flash('User updated successfully.', 'success')
            return redirect(url_for('list_users'))
        except Exception:
            db.session.rollback()
            flash('Something went wrong. Please try again.', 'error')
            return render_template('user_edit.html', user=user)
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
    """Create: add course (Segment 7). Validation + Flash (Segment 3)."""
    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        description = (request.form.get('description') or '').strip()
        teacher_id_raw = request.form.get('teacher_id', '').strip()

        # Backend validation (Segment 3)
        if not title:
            flash('Course title is required.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html', teachers=teachers, title=title, description=description)
        if not teacher_id_raw:
            flash('Please select a teacher.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html', teachers=teachers, title=title, description=description)
        try:
            teacher_id = int(teacher_id_raw)
        except ValueError:
            flash('Invalid teacher selected.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html', teachers=teachers, title=title, description=description)
        teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
        if not teacher:
            flash('Invalid teacher selected.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html', teachers=teachers, title=title, description=description)

        try:
            course = Course(title=title, description=description, teacher_id=teacher_id)
            db.session.add(course)
            db.session.commit()
            flash('Course created successfully.', 'success')
            return redirect(url_for('list_courses'))
        except Exception:
            db.session.rollback()
            flash('Something went wrong. Please try again.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_form.html', teachers=teachers, title=title, description=description)
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('course_form.html', teachers=teachers)


@app.route('/course/<int:id>')
def course_detail(id):
    """Read: single course detail (Segment 8)."""
    course = Course.query.get_or_404(id)
    return render_template('course_detail.html', course=course)


@app.route('/course/edit/<int:id>', methods=['GET', 'POST'])
def course_edit(id):
    """Update: edit course (Segment 9). Validation + Flash (Segment 3)."""
    course = Course.query.get_or_404(id)
    if request.method == 'POST':
        title = (request.form.get('title') or '').strip()
        description = (request.form.get('description') or '').strip()
        teacher_id_raw = request.form.get('teacher_id', '').strip()

        # Backend validation (Segment 3)
        if not title:
            flash('Course title is required.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', course=course, teachers=teachers)
        if not teacher_id_raw:
            flash('Please select a teacher.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', course=course, teachers=teachers)
        try:
            teacher_id = int(teacher_id_raw)
        except ValueError:
            flash('Invalid teacher selected.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', course=course, teachers=teachers)
        teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
        if not teacher:
            flash('Invalid teacher selected.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', course=course, teachers=teachers)

        try:
            course.title = title
            course.description = description
            course.teacher_id = teacher_id
            db.session.commit()
            flash('Course updated successfully.', 'success')
            return redirect(url_for('list_courses'))
        except Exception:
            db.session.rollback()
            flash('Something went wrong. Please try again.', 'error')
            teachers = User.query.filter_by(role='teacher').all()
            return render_template('course_edit.html', course=course, teachers=teachers)
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
