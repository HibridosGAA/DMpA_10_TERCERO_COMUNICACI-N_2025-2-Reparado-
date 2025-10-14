import os
import json
from flask import Flask, render_template

# 1. Inicialización de la aplicación Flask
app = Flask(__name__)

@app.route('/')
def index():
    # 2. Obtener y parsear la configuración unificada de Firebase desde Render
    # Si la variable no existe (ej: en desarrollo local), usa valores por defecto
    full_config_json = os.environ.get(
        'FULL_FIREBASE_CONFIG_JSON',
        '{"appId": "default-app-id", "firebaseConfig": {}}'
    )
    
    try:
        config_data = json.loads(full_config_json)
        # Extraer los dos valores que necesita el JavaScript
        app_id = config_data.get('appId', 'default-app-id')
        firebase_config = json.dumps(config_data.get('firebaseConfig', {}))
    except json.JSONDecodeError:
        print("ERROR: La variable FULL_FIREBASE_CONFIG_JSON no es un JSON válido.")
        app_id = 'error-loading-config'
        firebase_config = '{}'

    # 3. Servir el HTML e inyectar las variables
    return render_template(
        'index.html',
        app_id=app_id,
        firebase_config=firebase_config
    )

# La función principal la maneja Gunicorn en Render, este bloque es opcional
if __name__ == '__main__':
    # Usado para pruebas locales, no se ejecuta en Render
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
