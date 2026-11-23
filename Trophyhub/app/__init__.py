import os, logging
from flask import Flask, request, render_template


def create_app():
    app = Flask(__name__, template_folder='views', static_folder='statics')
    app.config['SECRET_KEY'] = 'chave-secreta-trophyhub-dev'
    app.logger.setLevel(logging.INFO)

    # Registro dos Blueprints
    from app.controllers.authcontroller import auth_bp
    from app.controllers.maincontroller import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"Página não encontrada: {request.path}")
        return render_template('404.html'), 404
    
    return app