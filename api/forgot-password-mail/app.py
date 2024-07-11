from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración del correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'heroefuerte136@gmail.com'
app.config['MAIL_PASSWORD'] = 'yvod qgtf ukms szmt'  

mail = Mail(app)

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Generar el contenido del correo con el enlace de redirección
    msg = Message('Password Reset Request', sender=('Netolight Support', 'heroefuerte136@gmail.com'), recipients=[email])
    msg.html = '''
    <p>Click on the following link to reset your password:</p>
    <a href="http://localhost:8080/reset-password" style="display: inline-block; padding: 10px 20px; font-size: 16px; text-align: center; text-decoration: none; color: white; background-color: #007bff; border-radius: 5px;">Reset Password</a>
    '''
    
    try:
        mail.send(msg)
        return jsonify({'message': 'Password reset email sent'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)
