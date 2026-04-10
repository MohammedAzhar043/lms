import os

from flask import Flask, render_template

from models import db
from routes.config import BASE_DIR, Config


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'templates'),
        static_folder=os.path.join(BASE_DIR, 'static'),
    )
    app.config.from_object(config_class)
    db.init_app(app)

    from routes import api_routes
    from routes import auth_routes
    from routes import course_routes
    from routes import main_routes
    from routes import user_routes
    from routes import video_routes

    main_routes.register_routes(app)
    auth_routes.register_routes(app)
    user_routes.register_routes(app)
    course_routes.register_routes(app)
    video_routes.register_routes(app)
    api_routes.register_routes(app)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    with app.app_context():
        db.create_all()
        print('Database tables created (user, course).')

    return app
