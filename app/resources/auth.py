from flask import request, jsonify, url_for, current_app
from flask_restful import Resource
from app.models.user import User
from app.extensions import db, mail
from app.services.validators import validate_password, validate_email
from app.services.token import generate_confirmation_token
from flask_jwt_extended import create_access_token
from flask_mail import Message
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
        if not validate_email(email):
            return {"message": "El email no cumple los requisitos de seguridad. "
                               "Debe tener el formato de una dirección de email"}, 400
    
        # Validar la contraseña con la función definida
        if not validate_password(password):
            return {"message": "La contraseña no cumple los requisitos de seguridad. "
                               "Debe tener al menos 8 caracteres, 1 mayúscula, 1 minúscula, "
                               "1 número y 1 carácter especial."}, 400

        # Verificar si el email ya está registrado
        if User.query.filter_by(email=email).first():
            return {"message": "El email ya está registrado."}, 400

        # Crear el usuario, pero con confirmed=False
        new_user = User(email=email, password=password)
        new_user.confirmed = False  # Asegúrate de que el usuario no esté confirmado inicialmente
        db.session.add(new_user)
        db.session.commit()

        # Generar token de confirmación
        token = generate_confirmation_token(email)
        
        # Generar el link de confirmación, usando url_for para construir la URL (asumiendo que tienes un endpoint de confirmación)
        confirm_url = url_for("confirm_email", token=token, _external=True)
        
        # Preparar el mensaje de email
        subject = "Confirma tu email"
        html_body = f"""
            <p>Hola,</p>
            <p>Gracias por registrarte en QuestionsApp. Por favor, confirma tu email haciendo clic en el siguiente enlace:</p>
            <p><a href="{confirm_url}">{confirm_url}</a></p>
            <p>Si no te registraste, ignora este correo.</p>
        """
        msg = Message(subject=subject, recipients=[email], html=html_body)
        try:
            mail.send(msg)
            current_app.logger.info(f"Email de confirmación enviado a {email}")
        except Exception as e:
            current_app.logger.error(f"Error al enviar email: {e}")
            return {"message": "Registro realizado, pero fallo al enviar el email de confirmación."}, 500

        return {"message": f"Usuario {email} registrado exitosamente. Se ha enviado un email de confirmación."}, 201
        
        # En un entorno real, enviarías un email con este enlace. En desarrollo, podrías imprimirlo en la consola.
        #current_app.logger.info(f"Enlace de confirmación: {confirm_url}")

        #return {"message": f"Usuario {email} registrado exitosamente. Por favor, confirma tu email: {confirm_url}"}, 201


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
