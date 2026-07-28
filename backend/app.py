# app.py
from flask import Flask, render_template
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    app = Flask(__name__)

    # Tell Flask to trust proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    from routes import register_routes
    register_routes(app,None)
    #with app.app_context():
    #    db.create_all()

    #migrate = Migrate(app , db)

    return app

