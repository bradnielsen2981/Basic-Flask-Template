from flask import *
import sys, os, logging, datetime
from interfaces.databaseinterface import Database
from interfaces.hashing import *
from interfaces.helpers import *
from flask_cors import CORS
from werkzeug.utils import secure_filename

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
cors = CORS(app)
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10

# Configure the upload folder and allowed file extensions
UPLOAD_FOLDER = 'profilephotos'
QRCODE_FOLDER = 'qrcodes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QRCODE_FOLDER'] = QRCODE_FOLDER
app.config['SECRET_KEY'] = "Type in secret line of text"

# Function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

DATABASE = Database("database/karaoke.db", app.logger)

#use @cross_origin() after @app.route to allow external access 
#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/logout')
def logout():
    app.logger.info("Log out")
    session.clear()
    return redirect('./')

#admin page
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

#home page
@app.route('/home')
def home():

    if 'userid' not in session:
        return redirect('./')

    app.logger.info("Home")
    return render_template("home.html")

#login page
@app.route('/', methods=["GET","POST"])
def login():
    app.logger.info("Login")

    if 'permission' in session:
        if session['permission'] == 'admin':
            return redirect("./admin")
        else:
            return redirect("./home")

    message = "Please login"
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
        if results:
            userdetails = results[0] #row in the user table (Python Dictionary)
            if check_password(userdetails['password'], password):
                message = "Login Successful"

                session['permission'] = userdetails['permission']
                session['userid'] = userdetails['userid']
                session['name'] = userdetails['firstname'] + " " + userdetails['lastname']
                session['profilephoto'] = userdetails['profilephoto']

                if session['permission'] == 'admin':
                    return redirect('./admin')
                else:
                    return redirect('./home')
            else: 
                message = "Password incorrect"
        else:
            message = "User does not exist, email is incorrect!!"

    return render_template("login.html", message=message)

#register
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

                #UPLOAD A FILE
                filepath = ''
                app.logger.info(request.files)
                if 'file' in request.files:
                    
                    file = request.files['file']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        flash("File uploaded successfully")


                password = hash_password(password)
                DATABASE.ModifyQuery("INSERT INTO users (firstname, lastname, email, password, profilephoto) VALUES (?,?,?,?,?)", (firstname, lastname, email, password,filepath))
                message = "Success, users has been added"
                return redirect('./')

    return render_template("register.html", message=message)

#events page
@app.route('/events', methods=['GET','POST'])
def events():
    app.logger.info("Events")
    current_datetime = datetime.datetime.now()
    results = DATABASE.ViewQuery("SELECT * FROM events WHERE eventdatetime > ?", (current_datetime,))

    #check if there is permission to delete an event
    permission = False
    for result in results:
        if result['eventcreatorid'] == session['userid'] or session['permission'] == 'admin':
            permission = True

    if request.method == "POST":

        #add an event
        if "Add" in request.form:
            eventname = request.form['eventname']

            #change to datetime
            eventdate = request.form['eventdate']
            eventtime = request.form['eventtime']
            eventdatetime = datetime.datetime.strptime(eventdate + ' ' + eventtime, '%Y-%m-%d %H:%M')

            eventvenue = request.form['eventvenue']
            eventaddress = request.form['eventaddress']
            eventpostcode = request.form['eventpostcode']

            #get longitude and latitude if possible
            eventlongitude = 0
            eventlatitude = 0
            eventlatitude, eventlongitude = get_coordinates(eventaddress, eventpostcode)

            DATABASE.ModifyQuery("INSERT INTO events (eventname, eventdatetime, eventvenue, eventaddress, eventpostcode, eventlongitude, eventlatitude, eventcreatorid) VALUES (?,?,?,?,?,?,?,?)", (eventname, 
            eventdatetime, eventvenue, eventaddress, eventpostcode, eventlongitude, eventlatitude, session['userid']))

            #create a qrcode for the event
            eventid = DATABASE.ViewQuery("SELECT MAX(eventid) FROM events")[0]['MAX(eventid)']
            create_qrcode(eventid)

            return redirect(url_for('events'))

        #delete selected events
        elif "Delete" in request.form:
            selectedevents = request.form.getlist("selectedevents")
            for selectedeventid in selectedevents:
                creatorid = DATABASE.ViewQuery("SELECT eventcreatorid FROM events WHERE eventid = ?", (selectedeventid,))[0]['eventcreatorid']
                if creatorid == session['userid'] or session['permission'] == 'admin':
                    DATABASE.ModifyQuery("DELETE FROM events WHERE eventid = ?", (selectedeventid,))
                    DATABASE.ModifyQuery("DELETE FROM playlist WHERE eventid = ?", (selectedeventid,))

            return redirect(url_for('events'))

    return render_template("events.html", results=results, permission=permission)

#playlist page
@app.route('/playlist/<eventid>', methods=['GET','POST'])
def playlist(eventid):
    app.logger.info("Playlist")

    current_datetime = datetime.datetime.now() + datetime.timedelta(hours=5)
    eventdetails = DATABASE.ViewQuery("SELECT * FROM events WHERE eventid = ? AND eventdatetime > ?", (eventid, current_datetime))
    if eventdetails == None and session['permission'] != 'admin':
        return redirect(url_for('events')) #event has passed

    results = DATABASE.ViewQuery("SELECT * FROM playlist WHERE eventid = ? AND songcompleted=0 ORDER BY songsequenceno", (eventid,))

    #check if there is permission to delete an event
    permission = "user"
    if session['permission'] == 'admin':
        permission = "admin"
    elif eventdetails[0]['eventcreatorid'] == session['userid']:
        permission = "eventcreator"
    else:
        if results:
            for result in results:
                if result['songcreatorid'] == session['userid']:
                    permission = "songcreator"

    if request.method == "POST":
        if 'Add' in request.form:
            songname = request.form['songname']
            songartist = request.form['songartist']
            songperformers = request.form['songperformers']
            songdatetime = datetime.datetime.now()
            DATABASE.ModifyQuery("INSERT INTO playlist (songname, songartist, songperformers, songdatetime, eventid, songcreatorid) VALUES (?,?,?,?,?,?)", (songname, songartist, songperformers, songdatetime, eventid, session['userid']))
            DATABASE.ModifyQuery("UPDATE playlist SET songsequenceno = songid WHERE songid = (SELECT MAX(songid) FROM playlist WHERE eventid = ?)", (eventid,))
       
        else:
            if permission:
                selectedsongids = request.form.getlist("selectedsongs")
                for songid in selectedsongids:
                    if 'Delete' in request.form: #allow deletion of events by the creator
                        DATABASE.ModifyQuery("DELETE FROM playlist WHERE songid = ?", (songid,))
                    if 'Complete' in request.form: #allow deletion of events by the creator
                        DATABASE.ModifyQuery("UPDATE playlist SET songcompleted = 1 WHERE songid = ?", (songid,))

        return redirect(url_for('playlist', eventid=eventid))

    return render_template("playlist.html", results=results, permission=permission, eventdetails=eventdetails[0])

#return a profile photo
@app.route('/profilephotos/<filename>')
def serve_profilephoto(filename):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)): # Ensure the file exists
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        abort(404) # If the file does not exist, return a 404 error
    return

#return a profile photo
@app.route('/qrcodes/<filename>')
def serve_qrcode(filename):
    if os.path.exists(os.path.join(app.config['QRCODE_FOLDER'], filename)): # Ensure the file exists
        return send_from_directory(app.config['QRCODE_FOLDER'], filename)
    else:
        abort(404) # If the file does not exist, return a 404 error
    return

# Exit the web server
@app.route('/exit', methods=['GET','POST'])
def exit():
    app.logger.info("Exiting")
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return jsonify({'message':'Exiting'})

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True) #runs a local server
