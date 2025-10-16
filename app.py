from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'


users = []

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        # Save user
        users.append({
            'email': email,
            'username': username,
            'password': password,
            'user_type': user_type
        })

        flash('Registered successfully! Log in now.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']

    # Check if user exists
    for user in users:
        if user['username'] == username and user['password'] == password:
            session['username'] = username
            session['user_type'] = user['user_type']

            if user['user_type'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('tenant_dashboard'))

    flash('Invalid username or password!')
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html', username=session.get('username'))

@app.route('/tenant')
def tenant_dashboard():
    return render_template('tenant.html', username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True)
