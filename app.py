from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'mysecret'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    mail = db.Column(db.String(150), unique=True, nullable=False)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
class CurrentNcr(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    customer = db.Column(db.String(150), nullable=False)
    job_number = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Redirect from the homepage to the login page
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
        
        if not email.endswith('@gisy.com'):
            flash('Registration is only allowed with an @gisy.com email address.')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    filters = {
        "date_from": request.form.get('date_from'),
        "date_to": request.form.get('date_to'),
        "customer": request.form.getlist('customer'),
        "job_number": request.form.get('job_number'),
        "type": request.form.get('type')
    }
    
    query = CurrentNcr.query
    
    if request.method == 'POST':
        if filters["date_from"]:
            query = query.filter(CurrentNcr.date >= filters["date_from"])
        if filters["date_to"]:
            query = query.filter(CurrentNcr.date <= filters["date_to"])
        if filters["customer"]:
            query = query.filter(CurrentNcr.company.in_(filters["customer"]))
        if filters["job_number"]:
            query = query.filter(CurrentNcr.job_number.like(f"%{filters['job_number']}%"))
        if filters["type"]:
            query = query.filter(CurrentNcr.type.like(f"%{filters['type']}%"))

        entries = query.all()

        if not entries:
            flash('No entries found for the specified filters.')
    else:
        entries = query.all()
    entries = CurrentNcr.query.all() #is this going to be a problem when I run the app?

    return render_template('dashboard.html', entries=entries, filters=filters)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/data', methods=['GET'])
@login_required
def get_data():
    data = Data.query.filter_by(user_id=current_user.id).all()
    return jsonify([d.content for d in data])

@app.route('/create_database', methods=['GET', 'POST'])
@login_required
def create_database():
    if request.method == 'POST':
        date = request.form['date']
        customer = request.form['customer']
        job_number = request.form['job_number']
        type = request.form['type']
        
        new_ncr = CurrentNcr(date=date, customer=customer, job_number=job_number, type=type)
        db.session.add(new_ncr)
        db.session.commit()
        flash('New NCR entry created successfully.')
        return redirect(url_for('dashboard'))
    
    return render_template('create_database.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)