import os
from flask import Flask, render_template

# Configuración de la aplicación
app = Flask(__name__)

# --- Rutas de la Aplicación ---

@app.route('/')
def index():
    """Sirve la página principal que contiene el chat anónimo (index.html)."""
    # Flask busca automáticamente este archivo dentro de la carpeta 'templates'.
    return render_template('index.html') 


# --- Inicialización del Servidor ---

if __name__ == '__main__':
    # Obtiene el puerto del entorno (necesario para Render) o usa 5000 por defecto.
    port = int(os.environ.get('PORT', 5000))
    
    # Inicia la aplicación. Usar host='0.0.0.0' es obligatorio para Render.
    # En producción (Render), el servidor gunicorn será el que maneje el arranque.
    app.run(debug=False, host='0.0.0.0', port=port)
