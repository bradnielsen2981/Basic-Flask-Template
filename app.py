from flask import *

import sys
import logging

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__) #create flask object

logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/')
def login():
    app.logger.info("Login")
    return "<h1>Login</h1>"

@app.route('/register')
def register():
    return "Register"

@app.route('/home')
def home():
    return "Home"

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
