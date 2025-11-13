from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['UPLOAD_FOLDER'] = 'static/uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(255))
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    facilities = db.Column(db.Text, nullable=False)
    room_type = db.Column(db.String(100), nullable=False)
    rules = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(100), nullable=False)



class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    duration_of_stay = db.Column(db.String(50), nullable=False)
    move_in_date = db.Column(db.Date, nullable=False)
    room_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    room = db.relationship('Room', backref=db.backref('reservations', lazy=True))


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            session['user_type'] = user.user_type

            if user.user_type == 'landlord':
                return redirect(url_for('landlord'))
            else:
                return redirect(url_for('tenant_dashboard'))

        flash('Invalid username or password!', 'error')
        return redirect(url_for('login'))


    return render_template('login.html')
@app.route('/tenant_login', methods=['POST'])
def tenant_login():
    email = request.form['email']
    password = request.form['password']

    tenant = Tenant.query.filter_by(email=email).first()

    if tenant and tenant.password == password:
        session['tenant_id'] = tenant.id   # 👈 store tenant ID
        session['tenant_name'] = tenant.full_name
        flash('Login successful!', 'success')
        return redirect(url_for('tenant_dashboard'))
    else:
        flash('Invalid email or password', 'danger')
        return redirect(url_for('login_page'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists!', 'error')
            return redirect(url_for('register'))

        new_user = User(email=email, username=username, password=password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/landlord')
def landlord():
    if 'username' not in session or session['user_type'] != 'landlord':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    rooms = Room.query.all()  # Show added rooms
    return render_template('landlord.html', rooms=rooms)


@app.route('/addroom', methods=['GET', 'POST'])
def addroom():
    if 'username' not in session or session['user_type'] != 'landlord':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        photo_file = request.files['photo']
        filename = None

        if photo_file:
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(photo_path)

        new_room = Room(
            photo=filename,
            name=request.form['name'],
            price=request.form['price'],
            location=request.form['location'],
            facilities=request.form['facilities'],
            room_type=request.form['room_type'],
            rules=request.form['rules'],
            contact=request.form['contact']
        )

        db.session.add(new_room)
        db.session.commit()


        flash('✅ Room successfully uploaded!', 'success')
        return redirect(url_for('addroom'))

    return render_template('addroom.html')

@app.route('/landlord/approve/<int:reservation_id>', methods=['POST'])
def approve_reservation_ajax(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.status = 'Approved'
    db.session.commit()
    return jsonify({'success': True})

@app.route('/landlord/reject/<int:reservation_id>', methods=['POST'])
def reject_reservation_ajax(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.status = 'Rejected'
    db.session.commit()
    return jsonify({'success': True})


@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    # Only landlord can update status
    if 'username' not in session or session['user_type'] != 'landlord':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    reservation = Reservation.query.get_or_404(id)


    new_status = request.form.get('status')
    if new_status in ['Pending', 'Approved', 'Rejected']:
        reservation.status = new_status
        db.session.commit()
        flash(f'Reservation status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'error')

    return redirect(url_for('viewreservations'))

@app.route('/tenant')
def tenant_dashboard():
    if 'username' not in session or session['user_type'] != 'tenant':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    rooms = Room.query.all()
    return render_template('tenant.html', rooms=rooms)

@app.route('/reserve/<int:room_id>')
def reserve_room(room_id):
    if 'username' not in session or session['user_type'] != 'tenant':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    room = Room.query.get_or_404(room_id)
    tenant_name = session.get('username')
    tenant_contact = ""
    return render_template('add_reservation.html', room=room, tenant_name=tenant_name, tenant_contact=tenant_contact)


@app.route('/room_details/<int:room_id>')
def room_details(room_id):
    room = Room.query.get_or_404(room_id)
    return render_template('room_details.html', room=room)


@app.route('/reserve/<int:room_id>')
def reserve(room_id):
    room = Room.query.get_or_404(room_id)
    return render_template('reserve_room.html', room=room)

@app.route('/reserves')
def reserves():
    if 'username' not in session or session['user_type'] != 'tenant':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    reservations = Reservation.query.filter_by(tenant_id=user.id).all()
    return render_template('reservation_status.html', reservations=reservations)

@app.route('/reservation_status')
def reservation_status():
    tenant_id = session.get('tenant_id')
    user = User.query.filter_by(username=session['username']).first()
    reservations = Reservation.query.filter_by(tenant_id=user.id).all()

    return render_template('reservation_status.html', reservations=reservations)

@app.route('/submit_reservation/<room_name>', methods=['POST'])
def submit_reservation(room_name):
    if 'username' not in session or session['user_type'] != 'tenant':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))


    tenant = User.query.filter_by(username=session['username']).first()

    if not tenant:
        flash('User not found!', 'error')
        return redirect(url_for('login'))

    new_reservation = Reservation(
        tenant_id=tenant.id,
        room_name=room_name,
        full_name=request.form['tenant_name'],
        contact_number=request.form['tenant_contact'],
        duration_of_stay=request.form['duration'],
        move_in_date=datetime.strptime(request.form['move_in_date'], '%Y-%m-%d'),
        room_id=request.form.get('room_id'),
        status='Pending'
    )

    db.session.add(new_reservation)
    db.session.commit()

    return redirect(url_for('reservation_status'))

@app.route('/tenant_reservations')
def tenant_reservations():
    if 'tenant_id' not in session:
        flash('Please log in first!', 'warning')
        return redirect(url_for('tenant_login'))

    tenant_id = session['tenant_id']
    reservations = Reservation.query.filter_by(tenant_id=tenant_id).all()

    return render_template('tenant_reservations.html', reservations=reservations)


@app.route('/reservations')
def viewreservations():
    if 'username' not in session:
        flash('Access denied!', 'error')
        return redirect(url_for('login'))

    reservations = Reservation.query.all()
    return render_template('viewres.html', reservations=reservations)

@app.route('/landlord/view_reservations')
def view_reservations():
    if 'landlord_id' not in session:
        flash('Please log in as a landlord to view reservations.', 'warning')
        return redirect(url_for('login'))

    landlord_id = session['landlord_id']
    reservations = Reservation.query.filter_by(landlord_id=landlord_id).all()
    return render_template('landlord_view_reservations.html', reservations=reservations)

@app.route('/add_reservation', methods=['POST'])
def add_reservation():
    tenant_name = request.form['tenant_name']
    tenant_contact = request.form['tenant_contact']
    room_id = request.form['room_id']

    new_reservation = Reservation(
        tenant_name=tenant_name,
        tenant_contact=tenant_contact,
        room_id=room_id,
        status='Pending'
    )

    db.session.add(new_reservation)
    db.session.commit()

    flash('Reservation request submitted successfully!', 'success')
    return redirect(url_for('tenant_dashboard'))

@app.route('/viewres')
def viewres():
    return render_template('viewres.html')

@app.route('/reveche')
def reveche():
    return render_template('reveche.html', room_name='Reveche')


@app.route('/quinny')
def quinny():
    return render_template('quinny.html', room_name='Quinny')

@app.route('/elora')
def elora():
    return render_template('elora.html', room_name='Elora')

@app.route('/silverio')
def silverio():
    return render_template('silverio.html', room_name='Silverio')

@app.route('/villasor')
def villasor():
    return render_template('villasor.html', room_name='Villasor')

@app.route('/paradise')
def paradise():
    return render_template('paradise.html', room_name='Paradise')

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

if __name__ == '__main__':
    app.run(debug=True)
