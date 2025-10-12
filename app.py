# -*- coding: utf-8 -*-
import random
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Configuración de la aplicación
app = Flask(__name__)
# Nota: La SECRET_KEY es necesaria para sesiones/seguridad en Flask
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

# Configuración de la base de datos (facemash.db en el directorio del proyecto)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facemash.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de la Persona
class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    # Guarda el nombre del archivo de imagen, que debe estar en la carpeta 'static'
    imagen_url = db.Column(db.String(200), nullable=False)
    # Puntuación Elo inicial
    elo_score = db.Column(db.Integer, default=1400)

    # Función __repr__ corregida para una representación legible
    def __repr__(self):
        return f"<Persona {self.nombre} | Elo: {self.elo_score}>"

# --- Función de Actualización Elo ---
K_FACTOR = 32 # Factor de ajuste para la volatilidad de la puntuación

def actualizar_elo(ganador, perdedor):
    
    r_a = ganador.elo_score
    r_b = perdedor.elo_score
    
    # 1. Calcular la probabilidad de victoria (Expected Score)
    prob_ganador = 1 / (1 + 10**((r_b - r_a) / 400))
    prob_perdedor = 1 / (1 + 10**((r_a - r_b) / 400)) 
    
    # 2. Aplicar la actualización de Puntuación
    # Resultado real S = 1 para el ganador
    nuevo_elo_ganador = r_a + K_FACTOR * (1 - prob_ganador)
    # Resultado real S = 0 para el perdedor
    nuevo_elo_perdedor = r_b + K_FACTOR * (0 - prob_perdedor)
    
    # 3. Guardar las nuevas puntuaciones redondeadas
    ganador.elo_score = int(round(nuevo_elo_ganador))
    perdedor.elo_score = int(round(nuevo_elo_perdedor))
    
    db.session.commit()

# --- Rutas y Lógica de la Aplicación ---

@app.route('/')
def index():
    # Obtener todas las personas
    personas = Persona.query.all()
    
    if len(personas) < 2:
        # Mensaje de error útil si la DB no se ha poblado correctamente
        return "ERROR: La base de datos no tiene suficientes personas. Asegúrate de haber subido el código, borrado 'facemash.db' y ejecutado 'inicializar_db()' en la consola Bash."
        
    # Seleccionar dos personas distintas al azar para votar
    persona_a, persona_b = random.sample(personas, 2)
    
    return render_template('index.html', persona_a=persona_a, persona_b=persona_b)

@app.route('/vote', methods=['POST'])
def vote():
    # El formulario envía el ID del ganador y perdedor
    ganador_id = request.form.get('ganador_id')
    perdedor_id = request.form.get('perdedor_id')
    
    if ganador_id and perdedor_id:
        ganador = Persona.query.get(ganador_id)
        perdedor = Persona.query.get(perdedor_id)
        
        if ganador and perdedor:
            actualizar_elo(ganador, perdedor)
            
    # Redirigir a la página principal para un nuevo par de votación
    return redirect(url_for('index'))

@app.route('/ranking')
def ranking():
    # Obtener todas las personas ordenadas por Elo descendente (el más alto primero)
    top_personas = Persona.query.order_by(Persona.elo_score.desc()).all()
    return render_template('ranking.html', personas=top_personas)

# --- INICIALIZACIÓN DE LA APLICACIÓN (PARA CREAR Y POBLAR LA DB) ---

def inicializar_db():
    
    # 1. LISTA DE MAPEO DEFINITIVA: (NOMBRE, NOMBRE_DEL_ARCHIVO_DE_IMAGEN)
    # NOTA: Debes asegurar que los archivos p1.jpg a p48.jpg existan en la carpeta 'static/'
    datos_personas = [
        ("ALEXIA", "p1.jpg"), 
        ("ASTRID ORIANA", "p2.jpg"), 
        ("BELINDA SHAMIRA", "p3.jpg"), 
        ("BIOMAYRA SHOANA", "p4.jpg"), 
        ("CAMILA JADIYÉH", "p5.jpg"), 
        ("GRISEL NATALY", "p6.jpg"), 
        ("RUTH KARINA", "p7.jpg"), 
        ("CIELO BELEN", "p8.jpg"), 
        ("CLARIBETH ALISSON", "p9.jpg"), 
        ("DARLEIN DAFNNE", "p10.jpg"), 
        ("DIANA ESMERALDA", "p11.jpg"), 
        ("EMILY JHONSU", "p12.jpg"), 
        ("ESTHEFANNY ARIANA", "p13.jpg"), 
        ("ESTHER", "p14.jpg"), 
        ("FABIOLA NICOLL", "p15.jpg"), 
        ("GLEIDY", "p16.jpg"), 
        ("GUIOMARA BRITTANY", "p17.jpg"), 
        ("JENNIFER LUCERO", "p18.jpg"), 
        ("JHOSELIN DELCIELO", "p19.jpg"), 
        ("KAROL ROSSELL", "p20.jpg"), 
        ("KATHERINA ALEXANDRA", "p21.jpg"), 
        ("KIARA DANIELA", "p22.jpg"), 
        ("LEIDY ORIANA", "p23.jpg"), 
        ("LEISLY MARINA", "p24.jpg"), 
        ("LEISLY EVANYELIN", "p25.jpg"), 
        ("MARIA ESTHER", "p26.jpg"), 
        ("MARY MIRIAM", "p27.jpg"), 
        ("MELISSA ALEXSANDRA", "p28.jpg"), 
        ("MELISSA ROSARIO", "p29.jpg"), 
        ("MILAGROS BRISAYDA", "p30.jpg"), 
        ("NATALY MARIBEL", "p31.jpg"), 
        ("NYKOLE LUCIANA", "p32.jpg"), 
        ("OSHIN MICHELLY", "p33.jpg"), 
        ("PEYTON STACEY", "p34.jpg"), 
        ("RITA SARIANAROUSSE", "p35.jpg"), 
        ("SANDY ENADINE", "p36.jpg"), 
        ("SARA YANET", "p37.jpg"), 
        ("SARAI MARGOTH", "p38.jpg"), 
        ("SHERLY NICOLE", "p39.jpg"), 
        ("SOLEDAD ROCIO", "p40.jpg"), 
        ("GLENY YESENIA", "p41.jpg"), 
        ("VENUS MARIADEL CIELO", "p42.jpg"), 
        ("VERONICA", "p43.jpg"), 
        ("YAQUELIN MARIALIZ", "p44.jpg"), 
        ("YASMIN NATSUMI", "p45.jpg"), 
        ("ZOE DANAEALEJANDRA", "p46.jpg"), 
        ("MILAGROS NOEMI", "p47.jpg"), 
        ("NUEVA", "p48.jpg")
    ]
    
    with app.app_context():
        db.create_all()
        
        # Poblamos la DB con datos de prueba si está vacía
        if not Persona.query.first():
            personas = []
            
            # Recorremos la lista de mapeo para crear los objetos Persona
            for nombre, url_foto in datos_personas:  
                
                personas.append(
                    Persona(nombre=nombre, imagen_url=url_foto, elo_score=1400)
                )

            db.session.add_all(personas)
            db.session.commit()
            print(f"Base de datos poblada con éxito con {len(datos_personas)} personas.")


# La inicialización se ejecuta aquí
inicializar_db()

if __name__ == '__main__':
    app.run(debug=True)
