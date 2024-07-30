from flask import *
import sys
import logging

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10
app.config['SECRET_KEY'] = "I am a secret key"

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    app.logger.info("Login")
    if request.method == 'POST': #something has been posted

        email = request.form['email'] #python dictionaries
        password = request.form['password']

        if email == 'admin@admin' and password == 'admin':
            session['username'] = "Mr Nielsen"
            session['userid'] = 1
            session['permission'] = "admin" #user or admin
            
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
            return "All hail to the admin!!!"
    else:
        return redirect('/')

@app.route('/register', method=['GET','POST']) #turn url on to receive data
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        passwordconfirm = request.form['passwordconfirm']
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
