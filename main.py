from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = "PepoleAreNotBlack"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.set_password(password)
        self.is_admin = is_admin

@app.route("/", methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('home.html')
    else:
        return render_template('login.html', message="")

@app.route("/register", methods=['POST','GET'])
def register():
    if request.method == 'POST':
        try:
            new_user = User(
                username=request.form['username'],
                password=request.form['password']
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            return render_template('register.html', message="User already exists")
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', message="Registration failed")
    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    u = request.form['username']
    p = request.form['password']
    user = User.query.filter_by(username=u).first()
    
    if user and user.check_password(p):
        session['logged_in'] = True
        session['is_admin'] = user.is_admin
        return redirect('/admin/')
    return render_template('login.html', message="Incorrect Details")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/')
def admin():
    if not session.get('is_admin') or not session.get('logged_in'):
        return redirect('/')
    return render_template('admin.html')

@app.route('/admin/users')
def admin_users():
    if not session.get('is_admin') or not session.get('logged_in'):
        return redirect('/')
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/change_password', methods=['POST'])
def admin_change_password():
    if not session.get('is_admin') or not session.get('logged_in'):
        return redirect('/')
    
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    user = db.session.get(User, user_id)
    
    if user:
        user.set_password(new_password)
        db.session.commit()
    
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<username>', methods=['GET', 'POST'])
def admin_user(username):
    if not session.get('is_admin') or not session.get('logged_in'):
        return redirect('/')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return render_template('404.html'), 404
    
    if request.method == 'POST':
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_users'))
    
    return render_template('admin_user.html', user=user)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        

        ADMIN_USERNAME = "admin"
        ADMIN_PASSWORD = "wyrewolwerowanyrewolwerowiecwyrewolwerowalwyrewolwerowanegorewolwerowca"
        
        if not User.query.filter_by(username=ADMIN_USERNAME).first():
            admin_user = User(
                username=ADMIN_USERNAME,
                password=ADMIN_PASSWORD,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user '{ADMIN_USERNAME}' created successfully!")

    app.run(host='0.0.0.0', port='5000', debug=True)