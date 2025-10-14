# -*- coding: utf-8 -*-
import random
import os
import click 

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc 
from whitenoise import WhiteNoise 

# Configuración de la aplicación
app = Flask(__name__)
# Usamos 'session' para guardar el estado de login, por eso necesitamos la SECRET_KEY
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_de_emergencia')

# --- CONFIGURACIÓN DE BASE DE DATOS PARA RENDER (POSTGRESQL) ---
db_url = os.environ.get('DATABASE_URL', 'sqlite:///facemash.db')

# Corrección del formato de la URL de PostgreSQL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# -----------------------------------------------------------

# Aplicar WhiteNoise para servir la carpeta 'static'
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', index_file=True)


# Inicializamos SQLAlchemy
db = SQLAlchemy()
db.init_app(app) 

# Modelo de la Persona
class Persona(db.Model):
    __tablename__ = 'persona' 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    imagen_url = db.Column(db.String(200), nullable=False)
    genero = db.Column(db.String(1), nullable=False) 
    elo_score = db.Column(db.Integer, default=1400)

    def __repr__(self):
        return f"<Persona {self.nombre} ({self.genero}) | Elo: {self.elo_score}>"

# --- Función de Actualización Elo ---
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

# NUEVA RUTA DE LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Obtiene el código de acceso seguro de las variables de entorno
    ACCESS_CODE = os.environ.get('ACCESS_CODE', '1234') # '1234' es un fallback local

    if request.method == 'POST':
        submitted_code = request.form.get('code')
        if submitted_code == ACCESS_CODE:
            # Si el código es correcto, marca la sesión como autenticada
            session['logged_in'] = True
            flash("Acceso exitoso. ¡A votar!")
            return redirect(url_for('elegir_categoria'))
        else:
            flash("Código de acceso incorrecto.", 'error')
            
    return render_template('login.html')

@app.route('/')
def elegir_categoria():
    """Ruta inicial que permite al usuario elegir entre Hombres y Mujeres."""
    # REDIRECCIONAR si el usuario no ha iniciado sesión
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    return render_template('inicio.html') 

@app.route('/vote/<genero>')
def index(genero):
    """Ruta para votar. Filtra por el género seleccionado ('H' o 'M')."""
    # REDIRECCIONAR si el usuario no ha iniciado sesión
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if genero not in ['H', 'M']:
        return redirect(url_for('elegir_categoria'))

    personas = Persona.query.filter_by(genero=genero).all() 
    
    if len(personas) < 2:
        return "ERROR: La base de datos no tiene suficientes personas en la categoría."
        
    persona_a, persona_b = random.sample(personas, 2)
    
    return render_template('index.html', persona_a=persona_a, persona_b=persona_b, genero=genero)

@app.route('/vote', methods=['POST'])
def vote():
    """Procesa el voto y redirige al voto de la misma categoría."""
    # REDIRECCIONAR si el usuario no ha iniciado sesión
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    ganador_id = request.form.get('ganador_id')
    perdedor_id = request.form.get('perdedor_id')
    genero = request.form.get('genero') 
    
    if ganador_id and perdedor_id and genero:
        ganador = Persona.query.get(ganador_id)
        perdedor = Persona.query.get(perdedor_id)
        
        if ganador and perdedor:
            actualizar_elo(ganador, perdedor)
            
    return redirect(url_for('index', genero=genero))

@app.route('/ranking/<genero>')
def ranking(genero):
    """Muestra el ranking filtrado por el género seleccionado."""
    # El ranking NO requiere login
    if genero not in ['H', 'M']:
        return redirect(url_for('elegir_categoria'))

    top_personas = Persona.query.filter_by(genero=genero).order_by(desc(Persona.elo_score)).all()
    
    titulo = "Hombres" if genero == 'H' else "Mujeres"
    return render_template('ranking.html', personas=top_personas, genero=genero, titulo=titulo)

@app.route('/logout')
def logout():
    """Cierra la sesión y redirige al login."""
    session.pop('logged_in', None)
    flash("Sesión cerrada correctamente.")
    return redirect(url_for('login'))


# --- INICIALIZACIÓN DE LA BASE DE DATOS COMO COMANDO DE FLASK ---

def get_data():
    """Retorna los datos de hombres y mujeres."""
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
    
    # Lista de 48 nombres de HOMBRES (CORREGIDO DE .JPG A .JPEG)
    datos_hombres = [
        ("DERLIN AARON", "p49.jpeg"), ("DEYVIS EMERSON", "p50.jpeg"), ("EDGAR LUDWYN", "p51.jpeg"), 
        ("EDSON RENE", "p52.jpeg"), ("EDY GROVER", "p53.jpeg"), ("EMANUEL TONY", "p54.jpeg"), 
        ("FERNANDO AMILCAR", "p55.jpeg"), ("FERNANDO", "p56.jpeg"), ("GENPIER SHERWIN", "p57.jpeg"), 
        ("HANS ANDRE", "p58.jpeg"), ("HUGO GABRIEL", "p59.jpeg"), ("JAIME ANGELINO", "p60.jpeg"), 
        ("JAREM ISAAC", "p61.jpeg"), ("JEAN PABLO", "p62.jpeg"), ("JEFFERSON RUBINHO", "p63.jpeg"), 
        ("JHOEL EMERSON", "p64.jpeg"), ("JHOEL SANTIAGO", "p65.jpeg"), ("JHON RONALD", "p66.jpeg"), 
        ("JHERLY JHELSIN", "p67.jpeg"), ("JOSE ABELARDO", "p68.jpeg"), ("JOSE BERNARDO", "p69.jpeg"), 
        ("JOSE JHOSEP", "p70.jpeg"), ("JOSE RAFAEL", "p71.jpeg"), ("JOSEPH YANDELIESUS", "p72.jpeg"), 
        ("JOSUE FABIAN", "p73.jpeg"), ("JUAN GABRIELAMARU", "p74.jpeg"), ("JUNIOR AUGUSTO", "p75.jpeg"), 
        ("LEONEL NIVARDO", "p76.jpeg"), ("LEONEL WILLY", "p77.jpeg"), ("MARCO ANTONIO", "p78.jpeg"), 
        ("MIKEL LENIN", "p79.jpeg"), ("NOE ABEL", "p80.jpeg"), ("PAUL DUBERLY", "p81.jpeg"), 
        ("PEDRO EMERSON", "p82.jpeg"), ("RICHARD JHEANFRANCO", "p83.jpeg"), ("SEBASTIAN BRIGAN", "p84.jpeg"), 
        ("SEBASTIAN MAURICIO", "p85.jpeg"), ("SHAMI MAGDIEL", "p86.jpeg"), ("TIAGO ALBERT", "p87.jpeg"), 
        ("VICTOR MANUEL", "p88.jpeg"), ("WILLIAM FERNANDO", "p89.jpeg"), ("YAN FRANCO", "p90.jpeg"), 
        ("YEFERSHON JHOSEP", "p91.jpeg"), ("YENSH LIONEL", "p92.jpeg"), ("YOSEF NEFTALI", "p93.jpeg"),
        ("CHICO 46 (RELLENO)", "p94.jpeg"), 
        ("CHICO 47 (RELLENO)", "p95.jpeg"), 
        ("CHICO 48 (RELLENO)", "p96.jpeg")
    ]
    return datos_mujeres, datos_hombres

@app.cli.command("init-db")
def init_db_command():
    """Crea las tablas de la DB y las puebla si no hay datos."""
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            click.echo("Tablas de la DB recreadas exitosamente.")

            if not Persona.query.first():
                datos_mujeres, datos_hombres = get_data()
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
                click.echo(f"Base de datos poblada con éxito con {len(personas)} personas.")
            else:
                click.echo("La base de datos ya contiene datos, no se repobló.")
                
        except Exception as e:
            click.echo(f"Error durante la inicialización de la DB: {e}")
            raise 

# Ejecución de la aplicación
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    with app.app_context():
        init_db_command() 
        
    app.run(debug=True, host='0.0.0.0', port=port)
