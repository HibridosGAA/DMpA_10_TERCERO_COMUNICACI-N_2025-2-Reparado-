# app.py: Aplicación Flask para MonkeySmash
# Incluye Login, manejo de persistencia e inyección de variables de Firebase.

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- CONFIGURACIÓN DE LA APLICACIÓN ---
app = Flask(__name__)
# Es CRÍTICO establecer la clave secreta para la seguridad de la sesión
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_smash_key_para_cambiar')

# --- VARIABLES DE ENTORNO PARA PERSISTENCIA ---
# Estas variables deben estar definidas en Render para la conexión a Firestore
FIREBASE_CONFIG_JSON = os.environ.get('FIREBASE_CONFIG_JSON', '{}')
APP_ID = os.environ.get('GHOSTEXT_APP_ID', 'default-monkey-smash-app-id') 

# --- CONFIGURACIÓN DE SEGURIDAD FIJA ---
CORRECT_CODE = "smash2025" # La clave que los usuarios DEBEN ingresar
AUTH_SESSION_KEY = "smash_authorized_user" 

# --- RUTAS ---

@app.route('/')
def welcome():
    """
    Ruta Raíz: Muestra el comunicado de bienvenida (welcome.html) antes del Login.
    Si el usuario ya está autenticado, lo salta y va a votar.
    """
    if session.get('auth_token') == AUTH_SESSION_KEY:
        return redirect(url_for('vote'))
        
    return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta para el formulario de login. Pide y verifica la contraseña.
    """
    # Si el usuario ya está autenticado, lo enviamos directamente a votar
    if session.get('auth_token') == AUTH_SESSION_KEY:
        return redirect(url_for('vote'))

    if request.method == 'POST':
        user_code = request.form.get('code')
        
        if user_code == CORRECT_CODE:
            session['auth_token'] = AUTH_SESSION_KEY
            flash('Acceso concedido. ¡A votar!', 'success')
            return redirect(url_for('vote'))
        else:
            flash('Código de acceso incorrecto. Inténtalo de nuevo.', 'error')
            
    # Si es GET o la clave es incorrecta, muestra el formulario de login
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cierra la sesión y vuelve a la pantalla de bienvenida."""
    session.pop('auth_token', None)
    # Redirige a la página principal con el comunicado
    return redirect(url_for('welcome')) 


@app.route('/vote')
def vote():
    """
    Página principal donde el usuario ve los candidatos y puede votar.
    """
    if session.get('auth_token') != AUTH_SESSION_KEY:
        flash('Debes iniciar sesión para votar.', 'error')
        # Redirigimos al comunicado si no hay auth
        return redirect(url_for('welcome')) 
        
    return render_template(
        'vote.html',
        app_id=APP_ID,
        firebase_config_json=FIREBASE_CONFIG_JSON
    )

@app.route('/ranking')
def ranking():
    """
    Página para mostrar el ranking de votos (solo para usuarios autenticados).
    """
    if session.get('auth_token') != AUTH_SESSION_KEY:
        flash('Debes iniciar sesión para ver el ranking.', 'error')
        # Redirigimos al comunicado si no hay auth
        return redirect(url_for('welcome')) 
        
    return render_template(
        'ranking.html',
        app_id=APP_ID,
        firebase_config_json=FIREBASE_CONFIG_JSON
    )


if __name__ == '__main__':
    # Configuración para que Flask se ejecute correctamente en Render (o localmente)
    port = int(os.environ.get('PORT', 5000))
    # Asegúrate de establecer la variable de entorno FLASK_SECRET_KEY en Render
    if app.secret_key == 'default_smash_key_para_cambiar':
        print("¡ADVERTENCIA DE SEGURIDAD! Usa una clave secreta fuerte en FLASK_SECRET_KEY.")
        
    app.run(host='0.0.0.0', port=port, debug=True)
