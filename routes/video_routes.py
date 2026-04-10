import os

from flask import abort, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from models import Course, Video, db
from routes.auth_decorators import login_requierd, role_required


def register_routes(app):
    @app.route('/course/<int:id>/video/create', methods=['GET', 'POST'])
    @login_requierd
    @role_required('teacher')
    def create_video(id):

        course = Course.query.get_or_404(id)

        if course.teacher_id != session.get('user_id'):
            abort(403)

        if request.method == 'POST':

            title = (request.form.get('title') or '').strip()
            file = request.files.get('file')

            if not title:
                flash('Title is required', 'error')
                return render_template('video_form.html', course=course)

            if not file or file.filename == '':
                flash('File is required', 'error')
                return render_template('video_form.html', course=course, title=title)

            filename = secure_filename(file.filename)

            if not filename:
                flash('Invalid file name', 'error')
                return render_template('video_form.html', course=course, title=title)

            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')

            os.makedirs(upload_dir, exist_ok=True)

            ext = os.path.splitext(filename)[1] or '.mp4'

            unique_name = f"{course.id}_{Video.query.filter_by(course_id=id).count() + 1}{ext}"

            file_path = os.path.join(upload_dir, unique_name)
            file.save(file_path)

            rel_path = f"uploads/videos/{unique_name}"

            video = Video(
                course_id=id,
                title=title,
                file_path=rel_path
            )

            db.session.add(video)
            db.session.commit()

            flash('Video added', 'success')

            return redirect(url_for('list_videos', id=id))

        return render_template('video_form.html', course=course)

    @app.route('/course/<int:id>/videos')
    @login_requierd
    def list_videos(id):

        course = Course.query.get_or_404(id)

        videos = Video.query.filter_by(
            course_id=id
        ).order_by(
            Video.order, Video.id
        ).all()

        return render_template('video_list.html', course=course, videos=videos)

    @app.route('/video/delete/<int:id>')
    @login_requierd
    @role_required('teacher')
    def delete_video(id):

        video = Video.query.get_or_404(id)
        course = Course.query.get_or_404(video.course_id)

        if course.teacher_id != session.get('user_id'):
            abort(403)

        db.session.delete(video)
        db.session.commit()

        flash('Video deleted.', 'success')

        return redirect(url_for('list_videos', id=course.id))
