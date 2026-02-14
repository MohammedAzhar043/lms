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

from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from models import db, User, Course
from werkzeug.security import generate_password_hash, check_password_hash

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

# Security (Segment 1): generate_password_hash when saving passwords;
# check_password_hash when verifying login (Segment 2 & 3).


def login_required(f):
    """Decorator: redirect to login if user not in session (Segment 3 - Auth)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to continue.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    """Decorator: abort 403 if session role does not match (Segment 4 - Auth)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                flash('Please log in to continue.', 'error')
                return redirect(url_for('login'))
            if session.get('role') != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def home():
    """Home page - uses base template (Segment 2)."""
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login: verify user, set session, redirect by role (Segment 1 - Auth)."""
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.', 'error')
            return render_template('login.html')

        session['user_id'] = user.id
        session['role'] = user.role
        session['username'] = user.username

        if user.role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        return redirect(url_for('student_dashboard'))

    return render_template('login.html')


@app.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():
    """Student dashboard placeholder (Segment 1 - Auth)."""
    return render_template('student_dashboard.html')


@app.route('/teacher/dashboard')
@login_required
@role_required('teacher')
def teacher_dashboard():
    """Teacher dashboard placeholder (Segment 1 - Auth)."""
    return render_template('teacher_dashboard.html')


@app.route('/logout')
def logout():
    """Logout: clear session, redirect to home (Segment 2 - Auth)."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/users')
@login_required
def list_users():
    """Read: list all users (Segment 2)."""
    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/courses')
@login_required
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
            hashed_password = generate_password_hash(password)
            user = User(username=username, email=email, password=hashed_password, role=role)
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
@login_required
def user_detail(id):
    """Read: single user detail (Segment 4)."""
    user = User.query.get_or_404(id)
    return render_template('user_detail.html', user=user)


@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
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
            user.password = generate_password_hash(password)
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
@login_required
def delete_user(id):
    """Delete: remove user (Segment 6). Redirect to list after delete."""
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))


@app.route('/course/create', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
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
@login_required
def course_detail(id):
    """Read: single course detail (Segment 8)."""
    course = Course.query.get_or_404(id)
    return render_template('course_detail.html', course=course)


@app.route('/course/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
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
@login_required
@role_required('teacher')
def course_delete(id):
    """Delete: remove course (Segment 9). Redirect to list after delete."""
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('list_courses'))


@app.errorhandler(403)
def forbidden(e):
    """Custom 403: Access denied (Segment 4 - Auth)."""
    return render_template('403.html'), 403


# Create all tables when app runs (first time)
with app.app_context():
    db.create_all()
    print('Database tables created (user, course).')


if __name__ == '__main__':
    app.run(debug=True)
