from flask import *
import sys
import logging

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/')
def login():
    app.logger.info("Login")
    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    app.logger.info("Register")

    if request.method == "POST":

        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['password']
        passwordconfirm = request.form['passwordconfirm']
        email = request.form['email']

        app.logger.info(email)

    return render_template("register.html", message="Please register")

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
