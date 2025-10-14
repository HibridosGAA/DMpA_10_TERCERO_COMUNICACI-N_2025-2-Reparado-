import os
import json
from flask import Flask, render_template, request, redirect, url_for, session

# --- Configuración de Flask ---
app = Flask(__name__)
# La clave secreta es necesaria para manejar las sesiones
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key_for_dev_change_it')

# Obtener la configuración de Firebase inyectada por el entorno
FIREBASE_CONFIG_JSON = os.environ.get('FIREBASE_CONFIG', '{}')
APP_ID = os.environ.get('APP_ID', 'default-app-id')

# --- CONFIGURACIÓN DE SEGURIDAD FIJA ---
# La contraseña que los usuarios DEBEN ingresar
CORRECT_PASSWORD = "SUPERSECRETO"
# El nombre interno de la sala que usaremos en Firestore (debe ser seguro)
SECRET_ROOM_KEY = "official_private_debate_room"


# --- Rutas de la Aplicación ---

@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Ruta para el formulario de login. Pide y verifica la contraseña.
    """
    error = None
    if request.method == 'POST':
        # Nota: Ahora pedimos 'password', no 'room_key'
        user_password = request.form.get('password')
        
        if user_password == CORRECT_PASSWORD:
            # Si la contraseña es correcta, usamos la clave fija para la sala
            session['room_key'] = SECRET_ROOM_KEY
            # Redirige a la lista de temas para esta sala secreta
            return redirect(url_for('topic_list', room=SECRET_ROOM_KEY))
        else:
            error = "Contraseña incorrecta. Inténtalo de nuevo."
        
    # Pasa el mensaje de error a la plantilla
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """
    Cierra la sesión y vuelve a la pantalla de login.
    """
    session.pop('room_key', None)
    return redirect(url_for('login'))


@app.route('/chat')
def topic_list():
    """
    Muestra la lista de temas (recuadros) para el debate.
    """
    room_key = request.args.get('room') or session.get('room_key')
    
    # Bloquea el acceso si no hay clave en la sesión (o si la clave no es la correcta)
    if not room_key or room_key != SECRET_ROOM_KEY:
        return redirect(url_for('login'))
        
    return render_template(
        'topics.html',
        app_id=APP_ID,
        firebase_config_json=FIREBASE_CONFIG_JSON
    )

@app.route('/room')
def chat_room():
    """
    Muestra la sala de chat para un tema y una clave de acceso específicos.
    """
    room_key = request.args.get('room')
    topic_id = request.args.get('topic')
    
    if not room_key or not topic_id:
        return redirect(url_for('topic_list', room=room_key))

    # Seguridad: Asegura que la clave de la URL coincide con la clave secreta fija
    if room_key != SECRET_ROOM_KEY:
        return redirect(url_for('login'))
    
    return render_template(
        'room.html',
        app_id=APP_ID,
        firebase_config_json=FIREBASE_CONFIG_JSON
    )


# Solo para desarrollo local
if __name__ == '__main__':
    if not os.environ.get('FLASK_SECRET_KEY'):
        import secrets
        app.secret_key = secrets.token_hex(16)
        print(f"Usando una clave secreta de desarrollo: {app.secret_key}")
    
    app.run(debug=True)
