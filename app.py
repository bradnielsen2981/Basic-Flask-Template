from flask import *

import sys
import logging

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__) #create flask object

logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/', methods=['GET','POST'])
def login():
    error = "Please login"
    app.logger.info("Login")
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
    return render_template("login.html", message=error)

@app.route('/register', methods=['GET','POST'])
def register():
    error = "Please register"
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        passwordconfirm = request.form['passwordconfirm']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        #check to see password < 8 characters
        if len(password) < 8:
            error = "Password is too short"
            return render_template("register.html", message=error)
        else:
            if passwordconfirm != password: #check to see if passwords match
                error = "Passwords do not match"
                return render_template("register.html", message=error)
            else:
                #flash("Registration successful, please login")
                return redirect('/')
    
    return render_template("register.html", message=error)

@app.route('/home')
def home():
    return "Home"

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
