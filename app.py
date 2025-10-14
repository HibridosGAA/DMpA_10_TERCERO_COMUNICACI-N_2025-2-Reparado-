# -*- coding: utf-8 -*-
import random
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_de_emergencia')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de la Persona
class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    imagen_url = db.Column(db.String(200), nullable=False)
    # NUEVA COLUMNA: Genero ('H' para Hombres, 'M' para Mujeres)
    genero = db.Column(db.String(1), nullable=False) 
    elo_score = db.Column(db.Integer, default=1400)

    def __repr__(self):
        return f"<Persona {self.nombre} ({self.genero}) | Elo: {self.elo_score}>"

# --- Función de Actualización Elo (Sin cambios) ---
K_FACTOR = 32

def actualizar_elo(ganador, perdedor):
    r_a = ganador.elo_score
    r_b = perdedor.elo_score
    prob_ganador = 1 / (1 + 10**((r_b - r_a) / 400))
    prob_perdedor = 1 / (1 + 10**((r_a - r_b) / 400)) 
    
    nuevo_elo_ganador = r_a + K_FACTOR * (1 - prob_ganador)
    nuevo_elo_perdedor = r_b + K_FACTOR * (0 - prob_perdedor)
    
    ganador.elo_score = int(round(nuevo_elo_ganador))
    perdedor.elo_score = int(round(nuevo_elo_perdedor))
    
    db.session.commit()

# --- Rutas y Lógica de la Aplicación ---

@app.route('/')
def elegir_categoria():
    """Ruta inicial que permite al usuario elegir entre Hombres y Mujeres."""
    return render_template('inicio.html') # NUEVO TEMPLATE

@app.route('/vote/<genero>')
def index(genero):
    """Ruta para votar. Filtra por el género seleccionado ('H' o 'M')."""
    if genero not in ['H', 'M']:
        return redirect(url_for('elegir_categoria'))

    # Filtrar personas por género
    personas = Persona.query.filter_by(genero=genero).all()
    
    if len(personas) < 2:
        return f"ERROR: La base de datos no tiene suficientes personas en la categoría {genero}. Total: {len(personas)}"
        
    # Seleccionar dos personas distintas al azar
    persona_a, persona_b = random.sample(personas, 2)
    
    return render_template('index.html', persona_a=persona_a, persona_b=persona_b, genero=genero)

@app.route('/vote', methods=['POST'])
def vote():
    """Procesa el voto y redirige al voto de la misma categoría."""
    ganador_id = request.form.get('ganador_id')
    perdedor_id = request.form.get('perdedor_id')
    genero = request.form.get('genero') # Obtenemos el género de la votación
    
    if ganador_id and perdedor_id and genero:
        ganador = Persona.query.get(ganador_id)
        perdedor = Persona.query.get(perdedor_id)
        
        if ganador and perdedor:
            actualizar_elo(ganador, perdedor)
            
    # Redirigir a la página de votación del MISMO género
    return redirect(url_for('index', genero=genero))

@app.route('/ranking/<genero>')
def ranking(genero):
    """Muestra el ranking filtrado por el género seleccionado."""
    if genero not in ['H', 'M']:
        return redirect(url_for('elegir_categoria'))

    top_personas = Persona.query.filter_by(genero=genero).order_by(Persona.elo_score.desc()).all()
    
    titulo = "Hombres" if genero == 'H' else "Mujeres"
    return render_template('ranking.html', personas=top_personas, genero=genero, titulo=titulo)

# --- INICIALIZACIÓN DE LA APLICACIÓN (PARA CREAR Y POBLAR LA DB) ---

def inicializar_db():
    
    # Lista de 48 nombres de MUJERES
    datos_mujeres = [
        ("ALEXIA", "p1.jpg"), ("ASTRID ORIANA", "p2.jpg"), ("BELINDA SHAMIRA", "p3.jpg"), 
        ("BIOMAYRA SHOANA", "p4.jpg"), ("CAMILA JADIYÉH", "p5.jpg"), ("GRISEL NATALY", "p6.jpg"), 
        ("RUTH KARINA", "p7.jpg"), ("CIELO BELEN", "p8.jpg"), ("CLARIBETH ALISSON", "p9.jpg"), 
        ("DARLEIN DAFNNE", "p10.jpg"), ("DIANA ESMERALDA", "p11.jpg"), ("EMILY JHONSU", "p12.jpg"), 
        ("ESTHEFANNY ARIANA", "p13.jpg"), ("ESTHER", "p14.jpg"), ("FABIOLA NICOLL", "p15.jpg"), 
        ("GLEIDY", "p16.jpg"), ("GUIOMARA BRITTANY", "p17.jpg"), ("JENNIFER LUCERO", "p18.jpg"), 
        ("JHOSELIN DELCIELO", "p19.jpg"), ("KAROL ROSSELL", "p20.jpg"), ("KATHERINA ALEXANDRA", "p21.jpg"), 
        ("KIARA DANIELA", "p22.jpg"), ("LEIDY ORIANA", "p23.jpg"), ("LEISLY MARINA", "p24.jpg"), 
        ("LEISLY EVANYELIN", "p25.jpg"), ("MARIA ESTHER", "p26.jpg"), ("MARY MIRIAM", "p27.jpg"), 
        ("MELISSA ALEXSANDRA", "p28.jpg"), ("MELISSA ROSARIO", "p29.jpg"), ("MILAGROS BRISAYDA", "p30.jpg"), 
        ("NATALY MARIBEL", "p31.jpg"), ("NYKOLE LUCIANA", "p32.jpg"), ("OSHIN MICHELLY", "p33.jpg"), 
        ("PEYTON STACEY", "p34.jpg"), ("RITA SARIANAROUSSE", "p35.jpg"), ("SANDY ENADINE", "p36.jpg"), 
        ("SARA YANET", "p37.jpg"), ("SARAI MARGOTH", "p38.jpg"), ("SHERLY NICOLE", "p39.jpg"), 
        ("SOLEDAD ROCIO", "p40.jpg"), ("GLENY YESENIA", "p41.jpg"), ("VENUS MARIADEL CIELO", "p42.jpg"), 
        ("VERONICA", "p43.jpg"), ("YAQUELIN MARIALIZ", "p44.jpg"), ("YASMIN NATSUMI", "p45.jpg"), 
        ("ZOE DANAEALEJANDRA", "p46.jpg"), ("MILAGROS NOEMI", "p47.jpg"), ("YANDELHY (NUEVA)", "p48.jpg")
    ]
    
    # Lista de 48 nombres de HOMBRES (45 tuyos + 3 de relleno)
    # Asumo que las imágenes de hombres son p49.jpg a p96.jpg
    datos_hombres = [
        ("DERLIN AARON", "p49.jpg"), ("DEYVIS EMERSON", "p50.jpg"), ("EDGAR LUDWYN", "p51.jpg"), 
        ("EDSON RENE", "p52.jpg"), ("EDY GROVER", "p53.jpg"), ("EMANUEL TONY", "p54.jpg"), 
        ("FERNANDO AMILCAR", "p55.jpg"), ("FERNANDO", "p56.jpg"), ("GENPIER SHERWIN", "p57.jpg"), 
        ("HANS ANDRE", "p58.jpg"), ("HUGO GABRIEL", "p59.jpg"), ("JAIME ANGELINO", "p60.jpg"), 
        ("JAREM ISAAC", "p61.jpg"), ("JEAN PABLO", "p62.jpg"), ("JEFFERSON RUBINHO", "p63.jpg"), 
        ("JHOEL EMERSON", "p64.jpg"), ("JHOEL SANTIAGO", "p65.jpg"), ("JHON RONALD", "p66.jpg"), 
        ("JHERLY JHELSIN", "p67.jpg"), ("JOSE ABELARDO", "p68.jpg"), ("JOSE BERNARDO", "p69.jpg"), 
        ("JOSE JHOSEP", "p70.jpg"), ("JOSE RAFAEL", "p71.jpg"), ("JOSEPH YANDELIESUS", "p72.jpg"), 
        ("JOSUE FABIAN", "p73.jpg"), ("JUAN GABRIELAMARU", "p74.jpg"), ("JUNIOR AUGUSTO", "p75.jpg"), 
        ("LEONEL NIVARDO", "p76.jpg"), ("LEONEL WILLY", "p77.jpg"), ("MARCO ANTONIO", "p78.jpg"), 
        ("MIKEL LENIN", "p79.jpg"), ("NOE ABEL", "p80.jpg"), ("PAUL DUBERLY", "p81.jpg"), 
        ("PEDRO EMERSON", "p82.jpg"), ("RICHARD JHEANFRANCO", "p83.jpg"), ("SEBASTIAN BRIGAN", "p84.jpg"), 
        ("SEBASTIAN MAURICIO", "p85.jpg"), ("SHAMI MAGDIEL", "p86.jpg"), ("TIAGO ALBERT", "p87.jpg"), 
        ("VICTOR MANUEL", "p88.jpg"), ("WILLIAM FERNANDO", "p89.jpg"), ("YAN FRANCO", "p90.jpg"), 
        ("YEFERSHON JHOSEP", "p91.jpg"), ("YENSH LIONEL", "p92.jpg"), ("YOSEF NEFTALI", "p93.jpg"),
        # Relleno para completar las 48 imágenes requeridas para consistencia:
        ("CHICO 46 (RELLENO)", "p94.jpg"), 
        ("CHICO 47 (RELLENO)", "p95.jpg"), 
        ("CHICO 48 (RELLENO)", "p96.jpg")
    ]

    # NOTA CRÍTICA: La base de datos DEBE ser borrada para que la nueva columna 'genero' se cree.
    with app.app_context():
        db.create_all()
        
        if not Persona.query.first():
            personas = []
            
            # 1. Agregar Mujeres
            for nombre, url_foto in datos_mujeres:  
                personas.append(
                    Persona(nombre=nombre, imagen_url=url_foto, elo_score=1400, genero='M')
                )
            
            # 2. Agregar Hombres
            for nombre, url_foto in datos_hombres:  
                personas.append(
                    Persona(nombre=nombre, imagen_url=url_foto, elo_score=1400, genero='H')
                )

            db.session.add_all(personas)
            db.session.commit()
            print(f"Base de datos poblada con éxito con {len(personas)} personas (48 Mujeres + 48 Hombres).")
        else:
            print("La base de datos ya contiene datos, no se repobló.")


# La inicialización se ejecuta aquí
inicializar_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
