from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, bcrypt, jwt
from flask_migrate import Migrate
from flask_restful import Api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    Migrate(app, db)

    # Inicializar Flask-RESTful API
    api = Api(app)

    # Registrar los endpoints
    from app.resources.auth import RegisterResource, LoginResource
    from app.resources.self_user import SelfUserResource
    
    api.add_resource(RegisterResource, '/register')
    api.add_resource(LoginResource, '/login')
    api.add_resource(SelfUserResource, '/self_user')
    api.add_resource(AdminUserResource, '/admin/user/<int:user_id>')
    api.add_resource(ProfileResource, '/profile', '/profile/<int:user_id>')
    api.add_resource(ConfirmEmailResource, '/confirm/<string:token>', endpoint='confirm_email')




    # Ruta de prueba
    @app.route("/")
    def home():
        return jsonify({"message": "API funcionando correctamente"}), 200
      
      
    # Inicializar Flask-Admin
    from app.admin import init_admin
    init_admin(app)

    return app

# Importar modelos para que sean detectados por Flask-Migrate
from app.models.user import User  
from app.models.profile import Profile
from app.resources.profile import ProfileResource
from app.resources.user import AdminUserResource
from app.resources.confirm import ConfirmEmailResource


