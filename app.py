import os
import json
from flask import Flask, render_template, request, redirect, url_for, session

# --- Configuración de Flask ---
app = Flask(__name__)
# La clave secreta es necesaria para manejar las sesiones (necesario para la clave de acceso)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key_for_dev_change_it')

# Obtener la configuración de Firebase inyectada por el entorno
# Si no está presente (por ejemplo, en desarrollo local), usa un JSON vacío
FIREBASE_CONFIG_JSON = os.environ.get('FIREBASE_CONFIG', '{}')
APP_ID = os.environ.get('APP_ID', 'default-app-id')


# --- Funciones de Utilidad ---

def get_firebase_config():
    """Devuelve la configuración de Firebase como objeto JSON."""
    return json.loads(FIREBASE_CONFIG_JSON)

# --- Rutas de la Aplicación ---

@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Ruta para el formulario de login. Pide una clave de acceso.
    """
    if request.method == 'POST':
        # La clave de acceso funciona como el identificador de la "sala" principal
        room_key = request.form.get('room_key')
        if room_key:
            # Guarda la clave en la sesión
            session['room_key'] = room_key
            # Redirige a la nueva ruta /chat (que ahora es la lista de temas)
            return redirect(url_for('topic_list', room=room_key))
        
    return render_template('login.html')

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
    NUEVA RUTA: Muestra la lista de temas (recuadros) para el debate.
    """
    room_key = request.args.get('room') or session.get('room_key')
    
    if not room_key:
        return redirect(url_for('login'))

    # Asegura que la clave de la URL coincide con la sesión o que la sesión existe
    if room_key != session.get('room_key'):
        return redirect(url_for('login'))
        
    # Renderiza la plantilla que muestra los recuadros de temas
    return render_template(
        'topics.html',
        app_id=APP_ID,
        firebase_config_json=FIREBASE_CONFIG_JSON
    )

@app.route('/room')
def chat_room():
    """
    NUEVA RUTA: Muestra la sala de chat para un tema y una clave de acceso específicos.
    Requiere 'room' (clave de acceso) y 'topic' (ID del tema).
    """
    room_key = request.args.get('room')
    topic_id = request.args.get('topic')
    
    if not room_key or not topic_id:
        # Si falta el ID del tema, volvemos a la lista de temas.
        return redirect(url_for('topic_list', room=room_key))

    # Seguridad: Asegura que la clave de la URL coincide con la sesión
    if room_key != session.get('room_key'):
        return redirect(url_for('login'))
    
    # Renderiza la plantilla que contiene el chat real
    return render_template(
        'room.html',
        app_id=APP_ID,
        firebase_config_json=FIREBASE_CONFIG_JSON
    )


# Solo para desarrollo local
if __name__ == '__main__':
    # Genera una clave secreta si no existe (solo para desarrollo)
    if not os.environ.get('FLASK_SECRET_KEY'):
        import secrets
        app.secret_key = secrets.token_hex(16)
        print(f"Usando una clave secreta de desarrollo: {app.secret_key}")
    
    # En desarrollo, el modo de debug es útil
    app.run(debug=True)
