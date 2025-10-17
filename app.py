from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages and sessions

# Database setup (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model (table)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# 🔑 Home / Login Page
@app.route('/')
def login():
    return render_template('login.html')

# 📝 Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        # Check if username or email exists in DB
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))

        # Add user to DB
        new_user = User(email=email, username=username, password=password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# 🔑 Login POST
@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        session['username'] = user.username
        session['user_type'] = user.user_type

        if user.user_type == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('tenant_dashboard'))

    flash('Invalid username or password!', 'error')
    return redirect(url_for('login'))

# 🔒 Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# 🏠 Tenant Dashboard
@app.route('/tenant')
def tenant_dashboard():
    if 'username' not in session or session['user_type'] != 'tenant':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))
    return render_template('tenant.html')

# 🛏 Reserve Pages
@app.route('/reveche')
def reveche():
    return render_template('reveche.html')

@app.route('/quinny')
def quinny():
    return render_template('quinny.html')

@app.route('/elora')
def elora():
    return render_template('elora.html')

@app.route('/silverio')
def silverio():
    return render_template('silverio.html')

@app.route('/villasor')
def villasor():
    return render_template('villasor.html')

@app.route('/paradise')
def paradise():
    return render_template('paradise.html')

# ℹ️ More Details Pages
@app.route('/reveched')
def reveched():
    return render_template('reveched.html')

@app.route('/quinnyd')
def quinnyd():
    return render_template('quinnyd.html')

@app.route('/elorad')
def elorad():
    return render_template('elorad.html')

@app.route('/silveriod')
def silveriod():
    return render_template('silveriod.html')

@app.route('/villasord')
def villasord():
    return render_template('villasord.html')

@app.route('/paradised')
def paradised():
    return render_template('paradised.html')

# 🛠 Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or session['user_type'] != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)
