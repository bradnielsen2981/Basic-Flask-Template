from flask import *
import sys
import logging
from interfaces.databaseinterface import Database

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10
app.config['SECRET_KEY'] = "I am a secret key"

DATABASE = Database("database/test.db", app.logger)

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/backdoor')
def backdoor():
    results = DATABASE.ViewQuery("SELECT * FROM users")    
    return jsonify(results)

@app.route('/', methods=['GET', 'POST'])
def login():
    app.logger.info("Login")
    if request.method == 'POST': #something has been posted
        email = request.form['email'] #python dictionaries
        password = request.form['password']

        results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        if results:
            user = results[0] #Python dictionary
            session['username'] = user['firstname'] + " " + user['lastname']
            session['userid'] = user['userid']
            session['permission'] = user['permission']
            
        app.logger.info("Login Successful")
        return redirect('/home') #TODO
    return render_template('login.html', message="Please login")

@app.route('/home')
def home():
    if 'userid' not in session:
        return redirect('/')
    app.logger.info("Home")
    return render_template('home.html', message="Welcome")

@app.route('/admin')
def admin():
    if 'permission' in session:
        if session['permission'] == 'admin': 
            app.logger.info("Admin")
            results = DATABASE.ViewQuery("SELECT * FROM users")  
            return render_template('admin.html', users=results)
    else:
        return redirect('/')

@app.route('/register', methods=['GET','POST']) #turn url on to receive data
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        passwordconfirm = request.form['passwordconfirm']

        if password != passwordconfirm:
            return render_template('register.html', message="Passwords do not match")

        results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
        if results:
            return render_template('register.html', message="Email already exists")

        DATABASE.ModifyQuery("INSERT INTO users (firstname, lastname, email, password, permission) VALUES (?, ?, ?, ?, ?)", (firstname, lastname, email, password, 'user'))
        return redirect('/')
    app.logger.info("Register")
    return render_template('register.html', message="Please register")

@app.route('/logout') #localhost:5000/register
def logout():
    session.clear()
    app.logger.info("Logging out")
    return redirect('/')

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
