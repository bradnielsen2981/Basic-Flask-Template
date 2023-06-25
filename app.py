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

        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['password']
        passwordconfirm = request.form['passwordconfirm']
        email = request.form['email']

        if password != passwordconfirm:
            message = "Error, passwords do not match"


    return render_template("register.html", message=message)

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
