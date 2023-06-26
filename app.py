from flask import *
import sys
import logging
from interfaces.databaseinterface import Database
from interfaces.hashing import *

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10
app.config['SECRET_KEY'] = "Type in secret line of text"

DATABASE = Database("database/test.db", app.logger)

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/backdoor')
def backdoor():
    app.logger.info("Backdoor")
    results = DATABASE.ViewQuery("SELECT * FROM users") #LIST OF PYTHON DICTIONARIES
    return jsonify(results)

@app.route('/admin', methods=["GET","POST"])
def admin():

    if 'permission' not in session:
        return redirect("./")
    else:
        if session['permission'] != 'admin':
            return redirect("./")

    results = DATABASE.ViewQuery("SELECT * FROM users")

    if request.method == "POST":
        selectedusers = request.form.getlist("selectedusers")
        for userid in selectedusers:
            if int(userid) != 1:
                DATABASE.ModifyQuery("DELETE FROM users WHERE userid = ?", (userid,))
        return redirect("./admin")

    app.logger.info("Admin")
    return render_template("admin.html", results=results)

@app.route('/home')
def home():

    if 'userid' not in session:
        return redirect('./')

    app.logger.info("Home")
    return render_template("home.html")

@app.route('/', methods=["GET","POST"])
def login():
    app.logger.info("Login")
    message = "Please login"
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
        if results:
            userdetails = results[0] #row in the user table (Python Dictionary)
            if password == userdetails['password']:
                message = "Login Successful"

                session['permission'] = userdetails['permission']
                session['userid'] = userdetails['userid']
                session['name'] = userdetails['firstname'] + " " + userdetails['lastname']

                if session['permission'] == 'admin':
                    return redirect('./admin')
                else:
                    return redirect('./home')
            else: 
                message = "Password incorrect"
        else:
            message = "User does not exist, email is incorrect!!"

    return render_template("login.html", message=message)

@app.route('/register', methods=['GET','POST'])
def register():
    app.logger.info("Register")
    message = "Please register"
    if request.method == "POST":

        firstname = request.form['fname']
        lastname = request.form['lname']
        password = request.form['password']
        passwordconfirm = request.form['passwordconfirm']
        email = request.form['email']

        if password != passwordconfirm:
            message = "Error, passwords do not match"
        else:
            results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
            if results:
                message = "Error, user already exists"
            else:
                DATABASE.ModifyQuery("INSERT INTO users (firstname, lastname, email, password) VALUES (?,?,?,?)", (firstname, lastname, email, password))
                message = "Success, users has been added"
                return redirect('./')

    return render_template("register.html", message=message)

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
