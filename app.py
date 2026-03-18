# FIX v2
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///portale.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nome = db.Column(db.String(100))
    cognome = db.Column(db.String(100))
    data_registrazione = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Corso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    colore = db.Column(db.String(7), default='#FF6B35')
    ordine = db.Column(db.Integer, default=0)
    moduli = db.relationship('Modulo', backref='corso', cascade='all, delete-orphan', order_by='Modulo.ordine')

class Modulo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    corso_id = db.Column(db.Integer, db.ForeignKey('corso.id'), nullable=False)
    ordine = db.Column(db.Integer, default=0)
    lezioni = db.relationship('Lezione', backref='modulo', cascade='all, delete-orphan', order_by='Lezione.ordine')

class Lezione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(200), nullable=False)
    descrizione = db.Column(db.Text)
    modulo_id = db.Column(db.Integer, db.ForeignKey('modulo.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    contenuto = db.Column(db.String(500))
    durata = db.Column(db.String(50))
    ordine = db.Column(db.Integer, default=0)
    completamento = db.Column(db.Integer, default=0)

class ProgressoUtente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lezione_id = db.Column(db.Integer, db.ForeignKey('lezione.id'), nullable=False)
    completato = db.Column(db.Boolean, default=False)
    data_completamento = db.Column(db.DateTime)
    user = db.relationship('User', backref='progressi')
    lezione = db.relationship('Lezione')

@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=request.form.get('remember', False))
            flash('Login effettuato!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        flash('Email o password non validi.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username, email, password, password_confirm = request.form['username'], request.form['email'], request.form['password'], request.form['password_confirm']
        if password != password_confirm: flash('Password non corrispondono.', 'error'); return render_template('register.html')
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first(): flash('Utente già esistente.', 'error'); return render_template('register.html')
        user = User(username=username, email=email, nome=request.form.get('nome',''), cognome=request.form.get('cognome',''))
        user.set_password(password); db.session.add(user); db.session.commit()
        flash('Registrazione completata!', 'success'); return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout(): logout_user(); flash('Logout effettuato.', 'info'); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    progressi = ProgressoUtente.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', lezioni_completate=len([p for p in progressi if p.completato]), totale_lezioni=Lezione.query.count())

@app.route('/lezione/<int:lezione_id>')
@login_required
def visualizza_lezione(lezione_id):
    lezione = Lezione.query.get_or_404(lezione_id)
    if lezione.tipo == 'video': return render_template('lezione_video.html', lezione=lezione)
    elif lezione.tipo == 'pdf': return render_template('lezione_pdf.html', lezione=lezione)
    return redirect(url_for('index'))

@app.route('/lezione/<int:lezione_id>/completa', methods=['POST'])
@login_required
def completa_lezione(lezione_id):
    progresso = ProgressoUtente.query.filter_by(user_id=current_user.id, lezione_id=lezione_id).first()
    if not progresso: progresso = ProgressoUtente(user_id=current_user.id, lezione_id=lezione_id, completato=True, data_completamento=datetime.utcnow()); db.session.add(progresso)
    else: progresso.completato = True; progresso.data_completamento = datetime.utcnow()
    db.session.commit(); flash('Lezione completata!', 'success'); return redirect(url_for('index'))

@app.route('/download/<filename>')
@login_required
def download_file(filename): return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index(): return render_template('index.html', corsi=Corso.query.order_by(Corso.ordine).all())

@app.route('/admin')
@login_required
def admin(): return render_template('admin.html', corsi=Corso.query.order_by(Corso.ordine).all())
@app.route('/debug-routes')
def debug_routes():
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    return '<br>'.join(sorted(routes))    

# ─── AGGIUNGI ────────────────────────────────────────────────────────────────

@app.route('/admin/corso/aggiungi', methods=['POST'])
@login_required
def aggiungi_corso():
    db.session.add(Corso(
        nome=request.form['nome'],
        descrizione=request.form.get('descrizione', ''),
        colore=request.form.get('colore', '#FF6B35'),
        ordine=request.form.get('ordine', 0)
    ))
    db.session.commit()
    flash('Corso aggiunto!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/modulo/aggiungi/<int:corso_id>', methods=['POST'])
@login_required
def aggiungi_modulo(corso_id):
    db.session.add(Modulo(
        nome=request.form['nome'],
        descrizione=request.form.get('descrizione', ''),
        corso_id=corso_id,
        ordine=request.form.get('ordine', 0)
    ))
    db.session.commit()
    flash('Modulo aggiunto!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/lezione/aggiungi/<int:modulo_id>', methods=['POST'])
@login_required
def aggiungi_lezione(modulo_id):
    contenuto = request.form['contenuto']
    if request.form['tipo'] == 'file' and 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            contenuto = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    db.session.add(Lezione(
        titolo=request.form['titolo'],
        descrizione=request.form.get('descrizione', ''),
        modulo_id=modulo_id,
        tipo=request.form['tipo'],
        contenuto=contenuto,
        durata=request.form.get('durata', ''),
        ordine=request.form.get('ordine', 0)
    ))
    db.session.commit()
    flash('Lezione aggiunta!', 'success')
    return redirect(url_for('admin'))

# ─── MODIFICA ────────────────────────────────────────────────────────────────

@app.route('/admin/corso/<int:id>/modifica', methods=['POST'])
@login_required
def modifica_corso(id):
    corso = Corso.query.get_or_404(id)
    corso.nome = request.form['nome']
    corso.descrizione = request.form.get('descrizione', '')
    corso.colore = request.form.get('colore', '#FF6B35')
    corso.ordine = request.form.get('ordine', 0)
    db.session.commit()
    flash('Corso aggiornato!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/modulo/<int:id>/modifica', methods=['POST'])
@login_required
def modifica_modulo(id):
    modulo = Modulo.query.get_or_404(id)
    modulo.nome = request.form['nome']
    modulo.descrizione = request.form.get('descrizione', '')
    modulo.ordine = request.form.get('ordine', 0)
    db.session.commit()
    flash('Modulo aggiornato!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/lezione/<int:id>/modifica', methods=['POST'])
@login_required
def modifica_lezione(id):
    lezione = Lezione.query.get_or_404(id)
    lezione.titolo = request.form['titolo']
    lezione.descrizione = request.form.get('descrizione', '')
    lezione.tipo = request.form['tipo']
    lezione.contenuto = request.form.get('contenuto', '')
    lezione.durata = request.form.get('durata', '')
    lezione.ordine = request.form.get('ordine', 0)
    db.session.commit()
    flash('Lezione aggiornata!', 'success')
    return redirect(url_for('admin'))

# ─── ELIMINA ─────────────────────────────────────────────────────────────────

@app.route('/admin/corso/<int:id>/elimina')
@login_required
def elimina_corso(id):
    obj = Corso.query.get_or_404(id)
    db.session.delete(obj)
    db.session.commit()
    flash('Corso eliminato!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/modulo/<int:id>/elimina')
@login_required
def elimina_modulo(id):
    obj = Modulo.query.get_or_404(id)
    db.session.delete(obj)
    db.session.commit()
    flash('Modulo eliminato!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/lezione/<int:id>/elimina')
@login_required
def elimina_lezione(id):
    obj = Lezione.query.get_or_404(id)
    db.session.delete(obj)
    db.session.commit()
    flash('Lezione eliminata!', 'success')
    return redirect(url_for('admin'))

# ─── ROUTE GENERICA (mantenuta per retrocompatibilità) ───────────────────────

@app.route('/admin/<tipo>/<int:id>/elimina')
@login_required
def elimina(tipo, id):
    if tipo == 'corso': obj = Corso.query.get_or_404(id)
    elif tipo == 'modulo': obj = Modulo.query.get_or_404(id)
    elif tipo == 'lezione': obj = Lezione.query.get_or_404(id)
    else: flash('Tipo non valido.', 'error'); return redirect(url_for('admin'))
    db.session.delete(obj); db.session.commit()
    flash('Eliminato!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
