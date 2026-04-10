from flask import jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from models import Course, Enrollment, User, db
from routes.auth_decorators import (
    _get_api_data,
    api_login_required,
    api_role_required,
)


def register_routes(app):
    @app.route('/api/courses')
    @api_login_required
    def api_list_courses():
        courses = Course.query.all()

        data = [
            {
                'id': c.id,
                'title': c.title,
                'description': c.description or '',
                'teacher_id': c.teacher_id,
                'status': c.status
            }
            for c in courses
        ]

        return jsonify({'status': 'success', 'data': data}), 200

    @app.route('/api/course/<int:id>')
    @api_login_required
    def api_course_detail(id):

        course = Course.query.get_or_404(id)

        if not course:
            return jsonify({'status': 'error', 'message': 'Course not found'}), 404

        data = {
            'id': course.id,
            'title': course.title,
            'description': course.description or '',
            'teacher_id': course.teacher_id,
            'teacher': course.teacher.username
        }

        return jsonify({'status': 'success', 'data': data}), 200

    @app.route('/api/users', methods=['POST'])
    def api_register():

        data = _get_api_data()

        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip()
        password = (data.get('password') or '')
        role = (data.get('role') or '').strip()

        if isinstance(username, list):

            username = (username[0] or '').strip() if username else ''

        if isinstance(email, list):
            email = (email[0] or '').strip() if email else ''

        if isinstance(password, list):
            password = (password[0]) if password else ''

        if isinstance(role, list):
            role = (role[0] or '').strip() if role else ''

        if not username:
            return jsonify({'status': 'error', 'message': 'username is required'}), 400

        if not email or '@' not in email:
            return jsonify({'status': 'error', 'message': 'Valid email is required'}), 400

        if not password or len(password) < 4:
            return jsonify({'status': 'error', 'message': 'password must be atleast 4 characters'}), 400

        if role not in ('student', 'teacher'):
            return jsonify({'status': 'error', 'message': 'role must be student or teacher'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'status': 'error', 'message': 'Username already taken'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'status': 'error', 'message': 'Email already registerd'}), 400

        try:
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                role=role
            )
            db.session.add(user)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'registration successful',
                'data': {'id': user.id}
            }), 201
        except Exception:

            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': 'Something went wrong'
            }), 500

    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = _get_api_data()
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': 'username and password required'
            }), 400

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401

        session['user_id'] = user.id
        session['role'] = user.role
        session['username'] = user.username

        session.permanent = True

        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'user_id': user.id,
                'role': user.role
            }
        }), 200

    @app.route('/api/users')
    @api_login_required
    def api_list_users():

        users = User.query.all()
        data = [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': u.role
            }
            for u in users
        ]

        return jsonify({
            'status': 'success',
            'data': data
        }), 200

    @app.route('/api/courses', methods=['POST'])
    @api_login_required
    @api_role_required('teacher')
    def api_create_course():

        data = _get_api_data()

        title = (data.get('title') or '').strip()
        description = (data.get('description') or '').strip()

        teacher_id = data.get('teacher_id') or session.get('user_id')

        if not title:
            return jsonify({
                'status': 'error',
                'message': 'Title is required'
            }), 400

        teacher = User.query.filter_by(id=teacher_id, role='teacher').first()

        if not teacher:
            return jsonify({
                'status': 'error',
                'message': 'Invalid teacher'
            }), 400

        try:
            course = Course(
                title=title,
                description=description,
                teacher_id=teacher_id
            )
            db.session.add(course)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Course Created',
                'data': {'id': course.id}
            }), 201
        except Exception:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': 'Something went wrong '
            }), 500

    @app.route('/api/courses/<int:id>', methods=['PUT'])
    @api_login_required
    @api_role_required('teacher')
    def api_update_course(id):

        course = Course.query.get(id)

        if not course:

            return jsonify({
                'status': 'error',
                'message': 'Course not found'
            }), 404

        if course.teacher_id != session.get('user_id'):
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403

        data = _get_api_data()

        title = (data.get('title') or course.title).strip()
        description = (data.get('description') or course.description or '').strip()

        if not title:
            return jsonify({
                'status': 'error',
                'message': 'Title is required'
            }), 400

        try:

            course.title = title
            course.description = description

            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'Course updadted'
            }), 200
        except Exception:

            db.session.rollback()

            return jsonify({
                'status': 'error',
                'message': 'something went wrong'
            }), 500

    @app.route('/api/courses/<int:id>', methods=['DELETE'])
    @api_login_required
    @api_role_required('teacher')
    def api_delete_course(id):

        course = Course.query.get(id)

        if not course:
            return jsonify({
                'status': 'error',
                'message': 'Course not found'
            }), 404

        if course.teacher_id != session.get('user_id'):
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403

        try:
            Enrollment.query.filter_by(course_id=id).delete()
            db.session.delete(course)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Course deleted'
            }), 200
        except Exception:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': 'something went wrong'
            }), 500

    @app.route('/api/enrollments', methods=['POST'])
    @api_login_required
    @api_role_required('student')
    def api_enroll():

        data = _get_api_data()

        course_id = data.get('course_id')

        if not course_id:

            return jsonify({
                'status': 'error',
                'message': 'course_id is required'
            }), 400

        course = Course.query.get(course_id)

        if not course:

            return jsonify({
                'status': 'error',
                'message': 'Course not found'
            }), 404

        user_id = session.get('user_id')

        existing = Enrollment.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()

        if existing:

            return jsonify({
                'status': 'error',
                'message': 'Already enrolled or pending'
            }), 400

        try:

            enrollment = Enrollment(
                user_id=user_id,
                course_id=course_id,
                status='pending'
            )

            db.session.add(enrollment)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'Enrollment requested',
                'data': {
                    'id': enrollment.id
                }
            }), 201

        except Exception:

            db.session.rollback()

            return jsonify({
                'status': 'error',
                'message': 'something went wrong'
            }), 500

    @app.route('/api/enrollments')
    @api_login_required
    def api_list_enrollments():

        user_id = session.get('user_id')
        role = session.get('role')
        course_id = request.args.get('course_id', type=int)
        if role == 'student':
            enrollments = Enrollment.query.filter_by(user_id=user_id).order_by(Enrollment.created_at.desc()).all()
        elif role == 'teacher' and course_id:
            course = Course.query.get(course_id)
            if not course or course.teacher_id != user_id:
                return jsonify({'status': 'error', 'message': 'Access denied'}), 403
            enrollments = Enrollment.query.filter_by(course_id=course_id).order_by(Enrollment.created_at.desc()).all()
        else:
            return jsonify({'status': 'error', 'message': 'Students: no params. Teachers: course_id required'}), 400
        data = [{'id': e.id, 'course_id': e.course_id, 'course_title': e.course.title, 'user_id': e.user_id, 'username': e.user.username, 'status': e.status} for e in enrollments]
        return jsonify({'status': 'success', 'data': data}), 200
