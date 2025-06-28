from flask import Flask as fs

def create_app(secrete_key: str):
    app = fs(__name__)
    app.config['SECRET_KEY'] = secrete_key
     
    # Add session configuration
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = 'filesystem'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app