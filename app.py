from flask import *
import sys
import logging
from interfaces.databaseinterface import Database


#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10

DATABASE = Database("database/test.db", app.logger)

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/backdoor')
def backdoor():
    app.logger.info("Backdoor")
    results = DATABASE.ViewQuery("SELECT * FROM users") #LIST OF PYTHON DICTIONARIES
    return jsonify(results)

@app.route('/')
def login():
    app.logger.info("Login")
    return render_template("login.html")

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

    return render_template("register.html", message=message)

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
