from flask import *
from interfaces.databaseinterface import Database
import sys
import logging
from datetime import datetime

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__) #create flask object

logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10

DATABASE = Database("database/test.db", app.logger)

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/backdoor')
def backdoor():
    app.logger.info("Backdoor")
    results = DATABASE.ViewQuery("SELECT * FROM users") #LIST OF PYTHON DICTIONARIES
    return jsonify(results)

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/', methods=['GET','POST'])
def login():
    error = "Please login"
    app.logger.info("Login")
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        userlist = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))

        if userlist == None:
            error = "No user exists with that email address"
            return render_template("login.html", message=error)
        else:
            user = userlist[0] #get user details
            p = user['password']
            if p != password:
                error = "Password incorrect!"
                return render_template("login.html", message=error)
            else:
                #save session details
                #update their lastaccess
                return redirect('/home')
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

        location = request.form['location']

        #CHECK IF EMAIL EXISTS

        #check to see password < 8 characters
        if len(password) < 8:
            error = "Password is too short"
            return render_template("register.html", message=error)
        else:
            if passwordconfirm != password: #check to see if passwords match
                error = "Passwords do not match"
                return render_template("register.html", message=error)
            else:
                #SUCCESS
                DATABASE.ModifyQuery("INSERT INTO users (email, password, firstname, lastname, lastaccess) VALUES (?,?,?,?,?)", (email,password,firstname,lastname, datetime.now()) );

                #flash("Registration successful, please login")
                return redirect('/')
    
    return render_template("register.html", message=error)

@app.route('/home')
def home():
    return render_template("home.html")

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
