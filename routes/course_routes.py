from flask import abort, flash, redirect, render_template, request, session, url_for

from models import Course, Enrollment, User, db
from routes.auth_decorators import login_requierd, role_required


def register_routes(app):
    @app.route('/student/dashboard')
    @login_requierd
    @role_required('student')
    def student_dashboard():
        return render_template('student_dashboard.html')

    @app.route('/teacher/dashboard')
    @login_requierd
    @role_required('teacher')
    def teacher_dashboard():
        return render_template('teacher_dashboard.html')

    @app.route('/course/create', methods=['GET', 'POST'])
    @login_requierd
    @role_required('teacher')
    def course_create():

        if request.method == 'POST':
            title = (request.form.get('title') or '').strip()
            descripation = (request.form.get('description') or '').strip()
            teacher_id_raw = (request.form.get('teacher_id') or '').strip()

            # backend validation
            if not title:
                flash('Course title is required', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_form.html', teachers=teachers, title=title, descripation=descripation)

            if not teacher_id_raw:
                flash('Please select a teacher', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_form.html', teachers=teachers, title=title, descripation=descripation)

            try:
                teacher_id = int(teacher_id_raw)
            except ValueError:
                flash('Invalid teacher selected', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_form.html', teachers=teachers, title=title, descripation=descripation)

            teacher = User.query.filter_by(id=teacher_id, role='teacher').first()

            if not teacher:
                flash('Invalid teacher selected', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_form.html', teachers=teachers, title=title, descripation=descripation)

            try:
                course = Course(title=title, description=descripation, teacher_id=teacher_id)
                db.session.add(course)
                db.session.commit()
                flash('Course created successfully', 'success')
                return redirect(url_for('list_courses'))
            except Exception:
                db.session.rollback()
                flash('something went wrong, please try again', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_form.html', teachers=teachers, title=title, descripation=descripation)

        teachers = User.query.filter_by(role='teacher').all()
        return render_template('course_form.html', teachers=teachers)

    @app.route('/courses')
    @login_requierd
    def list_courses():
        """Read: list all courses """
        courses = Course.query.all()
        return render_template('course_list.html', courses=courses)

    @app.route('/course/<int:id>')
    @login_requierd
    def course_detail(id):
        course = Course.query.get_or_404(id)
        user_enrollment = None

        if session.get('role') == 'student' and session.get('user_id'):
            user_enrollment = Enrollment.query.filter_by(user_id=session['user_id'], course_id=id).first()

        return render_template('course_detail.html', course=course, user_enrollment=user_enrollment)

    @app.route('/course/<int:id>/enroll', methods=['POST'])
    @login_requierd
    @role_required('student')
    def enroll_in_course(id):

        course = Course.query.get_or_404(id)
        user_id = session.get('user_id')
        existing = Enrollment.query.filter_by(user_id=user_id, course_id=id).first()
        if existing:
            flash('You have already requested enrollment or are enrolled.', 'error')
            return redirect(url_for('course_detail', id=id))
        enrollment = Enrollment(user_id=user_id, course_id=id, status='pending')
        db.session.add(enrollment)
        db.session.commit()
        flash('Enrollment requested. Waiting for teacher approval.', 'success')
        return redirect(url_for('course_detail', id=id))

    @app.route('/my-enrollments')
    @login_requierd
    @role_required('student')
    def my_enrollments():

        user_id = session.get('user_id')

        enrollments = Enrollment.query.filter_by(
            user_id=user_id
        ).order_by(
            Enrollment.created_at.desc()
        ).all()

        return render_template('my_enrollments.html', enrollments=enrollments)

    @app.route('/course/<int:id>/enrollments')
    @login_requierd
    @role_required('teacher')
    def course_enrollments(id):

        # 1.course exist
        course = Course.query.get_or_404(id)

        # 2.ensure teacher owns the course

        if course.teacher_id != session.get('user_id'):
            abort(403)
        # 3.check the enrollments

        enrollments = Enrollment.query.filter_by(
            course_id=id
        ).order_by(
            Enrollment.created_at.desc()
        ).all()

        # 4.send to template

        return render_template('course_enrollments.html', enrollments=enrollments, course=course)

    @app.route('/enrollment/<int:id>/approve', methods=['POST'])
    @login_requierd
    @role_required('teacher')
    def approve_enrollment(id):

        # 1.fetches enrollment record
        enrollment = Enrollment.query.get_or_404(id)

        course = Course.query.get_or_404(enrollment.course_id)

        # 2.verify teacher owns the course

        if course.teacher_id != session.get('user_id'):
            abort(403)

        # 3. status pending

        if enrollment.status != 'pending':
            flash('only pending enrollments can be approved', 'error')
            return redirect(url_for('course_enrollments', id=course.id))

        enrollment.status = 'enrolled'
        db.session.commit()

        flash('Enrollment approved.', 'success')
        return redirect(url_for('course_enrollments', id=course.id))

    @app.route('/enrollment/<int:id>/reject', methods=['POST'])
    @login_requierd
    @role_required('teacher')
    def reject_enrollment(id):
        # 1.fetches enrollment

        enrollment = Enrollment.query.get_or_404(id)

        course = Course.query.get_or_404(enrollment.course_id)

        # 2.validates teacher ownership

        if course.teacher_id != session.get('user_id'):
            abort(403)
        # 3.status pending

        if enrollment.status != 'pending':
            flash('only pending enrollments can be rejected.', 'error')
            return redirect(url_for('course_enrollments', id=course.id))

        # 4.status update to rejected
        enrollment.status = 'rejected'
        db.session.commit()

        flash('Enrollment rejected.', 'success')
        return redirect(url_for('course_enrollments', id=course.id))

    @app.route('/course/edit/<int:id>', methods=['GET', 'POST'])
    @login_requierd
    @role_required('teacher')
    def course_edit(id):
        course = Course.query.get_or_404(id)

        if request.method == 'POST':

            title = (request.form.get('title') or '').strip()
            description = (request.form.get('description') or '').strip()
            teacher_id_raw = (request.form.get('teacher_id') or '').strip()

            # backend validation
            if not title:
                flash('Course title is required', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_edit.html', teachers=teachers, course=course)

            if not teacher_id_raw:
                flash('Please select a teacher', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_edit.html', teachers=teachers, course=course)

            try:
                teacher_id = int(teacher_id_raw)
            except ValueError:
                flash('Invalid teacher selected', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_edit.html', teachers=teachers, course=course)

            teacher = User.query.filter_by(id=teacher_id, role='teacher').first()

            if not teacher:
                flash('Invalid teacher selected', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_edit.html', teachers=teachers, course=course)

            try:
                # Update
                course.title = title
                course.description = description
                course.teacher_id = teacher_id

                db.session.commit()
                flash('Course updated successfully.', 'success')
                return redirect(url_for('list_courses'))

            except Exception:
                db.session.rollback()
                flash('something went wrong, please try again', 'error')
                teachers = User.query.filter_by(role='teacher').all()
                return render_template('course_edit.html', teachers=teachers, course=course)

        # GET request
        teachers = User.query.filter_by(role='teacher').all()
        return render_template('course_edit.html', course=course, teachers=teachers)

    @app.route('/course/delete/<int:id>')
    @login_requierd
    @role_required('teacher')
    def course_delete(id):

        course = Course.query.get_or_404(id)
        db.session.delete(course)
        db.session.commit()
        return redirect(url_for('list_courses'))
