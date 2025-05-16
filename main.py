from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy
from wtforms import PasswordField, SubmitField

# Agrega esta clase de formulario
class LoginForm(FlaskForm):
    username = StringField('Correo electrónico', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

# objeto app
app = Flask(__name__)

# Configuración de seguridad
app.secret_key = 'clave_secreta'
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Configuración para la carga de imágenes
app.config['UPLOAD_FOLDER'] = 'static/imagenes'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Configuración de la base de datos (usando SQLAlchemy)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productos.db'
db = SQLAlchemy(app)

# Modelo de Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    imagen_url = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# Formulario WTForms
class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    marca = SelectField('Marca', choices=[
        ('hp', 'HP'),
        ('asus', 'Asus'),
        ('dell', 'Dell'),
        ('apple', 'Apple')
    ], validators=[DataRequired()])
    imagen = FileField('Imagen del Producto')

# Rutas de administración
@app.route('/admin/rentas')
def admin_rentas():
    productos = Producto.query.all()
    return render_template('admin_rentas.html', productos=productos)

@app.route('/admin/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        file = form.imagen.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        producto = Producto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            marca=form.marca.data,
            imagen_url=f'imagenes/{filename}'
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto creado exitosamente')
        return redirect(url_for('admin_rentas'))
    return render_template('form_producto.html', form=form)

@app.route('/admin/producto/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)

    if form.validate_on_submit():
        if form.imagen.data:
            file = form.imagen.data
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            producto.imagen_url = f'imagenes/{filename}'

        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.marca = form.marca.data

        db.session.commit()
        flash('Producto actualizado exitosamente')
        return redirect(url_for('admin_rentas'))

    return render_template('form_producto.html', form=form, producto=producto)

@app.route('/admin/producto/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente')
    return redirect(url_for('admin_rentas'))

# ruta llamado paginas
# llamar layout
@app.route('/')
def home():
    return render_template('layout.html')

# llamara rentas
CAROUSEL_FOLDERS = ['static/carousel_hp', 'static/carousel_dell', 'static/carousel_acer', 'static/carousel_apple','static/carousel_lenovo']  # Asegúrate de tener la carpeta de Apple

@app.route('/rentas')
def rentas():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para ver el catálogo')
        return redirect(url_for('login'))

    carousels_data = []
    for folder_path in CAROUSEL_FOLDERS:
        folder_name = os.path.basename(folder_path)
        carousel_name = folder_name.replace('carousel_', '').replace('_', ' ').title()
        brand = folder_name.replace('carousel_', '').lower()  # Obtiene la marca en minúsculas
        image_urls = []
        try:
            for img_name in os.listdir(folder_path):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    image_urls.append(url_for('static', filename=f'{folder_name}/{img_name}'))
            if image_urls:
                carousels_data.append({'name': carousel_name, 'images': image_urls, 'brand': brand})
        except FileNotFoundError:
            flash(f'La carpeta "{folder_path}" no se encontró.')

    return render_template('rentas.html', carousels_data=carousels_data)
# llamar desarrollo y creacion
@app.route('/desarrollo_y_creacion')
def desycre():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para ver esta página')
        return redirect(url_for('login'))
    return render_template('desycre.html')

# llamar soporte tecnico
@app.route('/soporte_tecnico')
def soptec():
    return render_template('soptec.html')

# llamar cotizacion web
@app.route('/cotizacion_web')
def cotweb():
    return render_template('cotweb.html')

# llamar rentas/hp440
@app.route('/rentas/hp-probook-440-g1')
def hp440():
    return render_template('pcs/hp440.html')

# llamar rentas/delloptiplex
@app.route('/rentas/dell-optiplex-750')
def dell750():
    return render_template('pcs/dell750.html')

# llamar rentas/asusrog
@app.route('/rentas/asus-rog')
def asusrog():
    return render_template('pcs/asusrog.html')

# llamar rentas/macbook
@app.route('/rentas/macbook-air')
def macbook():
    return render_template('pcs/macbook.html')

# info hp
@app.route('/rentas/info-hp')
def info_hp():
    return render_template('marc/hp.html')

# info asus
@app.route('/rentas/info-asus')
def info_asus():
    return render_template('marc/asus.html')

# inicio de sesion
usuarios = {}

# Crear usuario demo por defecto (para pruebas)
if not usuarios:
    usuarios['demo@bytecorp.com'] = generate_password_hash('ByteCorp123')
    print("Usuario demo creado: demo@bytecorp.com / ByteCorp123")

# llamar registro y registrar datos
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in usuarios:
            flash('El usuario ya existe')
        else:
            usuarios[username] = generate_password_hash(password)
            flash('Registro exitoso')
            return redirect(url_for('login'))
    return render_template('loging/registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Crea una instancia del formulario
    
    if form.validate_on_submit():  # Cambia a validación con WTForms
        username = form.username.data
        password = form.password.data
        user_pass = usuarios.get(username)

        if user_pass and check_password_hash(user_pass, password):
            session['usuario'] = username
            flash('Inicio de sesión exitoso')
            return redirect(url_for('admin_rentas'))
        else:
            flash('Usuario o contraseña incorrectos')
    
    return render_template('loging/login.html', form=form)  # Pasa el formulario al template
def bienvenido():
    if 'usuario' in session:
        flash('Bienvenid@ ' + session['usuario'])
    return ''

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Sesión cerrada exitosamente')
    return redirect(url_for('home'))

# Ruta protegida de ejemplo
@app.route('/perfil')
def perfil():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para ver esta página')
        return redirect(url_for('login'))
    return render_template('perfil.html')

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)



if __name__ == '__main__':
    app.run(debug=True)