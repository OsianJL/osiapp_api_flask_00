from flask import request, jsonify
from flask_restful import Resource
from app.models.user import User
from app.extensions import db
from app.services.validators import validate_password
from flask_jwt_extended import create_access_token
import datetime

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()

        # Verificar que se hayan enviado email y password
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return {"message": "Se requieren email y password"}, 400

        # Validar la contraseña con la función definida
        if not validate_password(password):
            return {"message": "La contraseña no cumple los requisitos de seguridad. "
                               "Debe tener al menos 8 caracteres, 1 mayúscula, 1 minúscula, "
                               "1 número y 1 carácter especial."}, 400

        # Verificar si el email ya está registrado
        if User.query.filter_by(email=email).first():
            return {"message": "El email ya está registrado."}, 400

        # Crear el usuario
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return {"message": "Usuario registrado exitosamente."}, 201


class LoginResource(Resource):
    def post(self):
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return {"message": "Se requieren email y password"}, 400

        # Buscar el usuario por email
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return {"message": "Credenciales inválidas"}, 401

        # Crear un token JWT
        # Definimos un tiempo de expiración (por ejemplo, 1 hora)
        expires = datetime.timedelta(hours=1)
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)

        return {"access_token": access_token}, 200
