# Bill of Lading Generator
# Author: YGJ

from flask import Flask, flash, render_template, redirect, request, session, make_response, send_file, url_for, flash, send_from_directory, current_app
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from xhtml2pdf import pisa
from datetime import datetime
import io
import os
from helpers import login_required
from itertools import zip_longest
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_wtf import FlaskForm
# from wtforms import StringField
# from wtforms.validators import DataRequired
import creds 


app = Flask(__name__)

# app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config['FLASH_MESSAGES_OPTIONS'] = {'timeout': 3}
app.config["SESSION_FILE_DIR"] = os.environ.get("SESSION_FILE_DIR")

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# # Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# app.config["USE_SESSION_FOR_NEXT"] = True
# Session(app)

##CREATE TABLE IN DB
# Organization Table

# Person Table
class Person(UserMixin, db.Model):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True)    
    username = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    password_hash = db.Column(db.String(1000))
    
    def __repr__(self):
        return '<Person {}>'.format(self.username)
    

@login_manager.user_loader
def load_user(user_id):
    return Person.query.get(int(user_id))

  
#Line below only required once, when creating DB. 
#db.create_all()
with app.app_context():    
    db.create_all()
    print("executed in context")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    # print(current_user)    
    if current_user.is_authenticated:
        return render_template("form.html")
    else:
        return render_template("login.html")


@app.route("/subscribe", methods = ['GET', 'POST'])
@login_required
def subscribe():
    print("Subscribe Request triggered")
    return render_template("subscribe.html")


@app.route("/login", methods = ['GET', 'POST'])
def login():      
    if request.method == "POST":
        email = request.form.get("email").lower().replace(" ", "")
        password = request.form.get("password")
        print("Login query \u2193 \n"+request.remote_addr + " - " + 
        str(datetime.now()) + " \u2193 \n"+  email)
        
        #check_password_hash(pwhash, password) 
        # where pwhash == hash in db, password == arguement password, returns true if matched
        if Person.query.filter_by(email=email).count() == 1:
            user = Person.query.filter_by(email=email).first()
            #print(Person.query.all())
        else:
            user = None

        # Valid email, there is one Person with this email in the DB
        if user:
            user_pwhash = user.password_hash
            person_id = user.id
            first_name = user.first_name
            arg_hash = check_password_hash(user_pwhash, password)
            print("Found email in database")
            #print(user)
            print("Password match == " + str(arg_hash))            
            # If authenticated, remember which user has logged in
            if arg_hash == True:
                is_logged_in = login_user(user)
                print("Is logged in check: " + str(is_logged_in))
                flash('Logged in successfully.', "success")
                print("? user.is_authenticated: " +str(user.is_authenticated))
                return render_template("form.html", first_name=first_name)
            else:
                # Password mismatch. FLash("Invalid email or password")
                flash("Invalid email or password", "warning")
                return render_template("login.html")
        
        elif not user:
            # No email in db. FLash("Invalid email or password")
            flash('Invalid username or password.', "warning")
            print("No person in DB with this email. Redirect to Registration")
            # print("Print is_authenticated ")
            # print(user.is_authenticated)
            return render_template("login.html")

        print("Login Request triggered")

    else:
        return render_template("login.html")


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == "POST":

        print("Register Request triggered")   
        # Get registration data
        first_name = request.form.get("first_name").replace(" ", "")
        last_name = request.form.get("last_name").replace(" ", "")
        username = request.form.get("username")
        email = request.form.get("email").lower().replace(" ", "")
        # display_name = request.form.get("display_name")
        password_hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        #print(password_hash)

        # SQL: write data into db
        # Set data
        person_update = Person(username=username, first_name=first_name,last_name=last_name,
                               email=email, password_hash=password_hash)
        
        # Checking database before registering
        if Person.query.filter_by(email=email).count() >0:
            print(first_name + " already exists")
            flash("Oops! "+ email + " already exists. If this is you, please log in.", "warning")            
            return render_template("register.html")

        elif Person.query.filter_by(email=email).count() == 0:
            print(Person.query.filter_by(email=email).count())
            flash("Welcome, " +first_name + ". You've signed up successfully.", "success")
            print(first_name + " did not exist. Registering user")
            db.session.add(person_update)
            db.session.commit()
            user = person_update
            is_logged_in = login_user(user)
            return render_template("form.html")
        
        else:
            flash("Unable to Register this user", "warning")
            print("Unable to Register this user")
            return render_template("register.html")

    else:
        return render_template("register.html")


@app.route("/logout", methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    print("Logout Request triggered")
    flash("Logged out successfully", "success")
    return render_template("login.html")


@app.route("/form", methods = ['GET', 'POST'])
@login_required
def form():
    print("Request triggered")
    
    if request.method == "POST":       
        # Getting values from the form
        your_company_name = str(request.form.get("your_company_name"))    
        your_company_address = str(request.form.get("your_company_address"))
        your_company_phone = str(request.form.get("your_company_phone"))
        dispatcher_name = str(request.form.get("dispatcher_name"))
        dispatcher_email = str(request.form.get("dispatcher_email"))
        dispatcher_phone = str(request.form.get("dispatcher_phone"))
        run_date = str(request.form.get("run_date"))
        dock = str(request.form.get("dock"))
        to_company = str(request.form.get("to_company"))
        bill_to = str(request.form.get("bill_to"))
        quantity = str(request.form.get("quantity"))
        weight = str(request.form.get("weight"))
        rate = str(request.form.get("rate"))
        equipment_details = str(request.form.get("equipment_details"))
        
        # Lists
        pickup_locations = request.form.getlist("pickup_location")
        pickup_times = request.form.getlist("pickup_time")
        delivery_locations = request.form.getlist("delivery_location")
        delivery_times = request.form.getlist("delivery_time")
        comments = request.form.getlist("comments")
        
        # Files
        try:
            logo = request.files["logo"]
            filename = secure_filename(logo.filename)
            logo_path = os.path.join(app.instance_path, filename)
            print(logo_path)
            logo.save(logo_path)
            print(logo_path)    
        except FileNotFoundError:
            print("Error getting logo. Caught FileNotFoundError")
        except IsADirectoryError:
            print("Did not upload a file. Caught isADirectoryError")        
             
        comments_formatted =  [x for x in comments if x != '']
        print(comments_formatted)        

        # Create a new list of dictionaries {"Address":value, "Time":value} for pickup locations
        pickup_tuples = list(zip_longest(pickup_locations, pickup_times, fillvalue="None"))
        delivery_tuples =list(zip_longest(delivery_locations, delivery_times, fillvalue="None"))
      
        # Create a list of dictionaries with pu_address and pu_time
        pickup_details =[]
        for t in pickup_tuples:
            temp_dict = {"pu_address":t[0],"pu_time":t[1]}
            pickup_details.append(temp_dict)    
        print ("pickup_details ↓")       
        print(pickup_details)
        
        # Create a new list of dictionaries {"Address":value, "Time":value} foe delivery locations
        delivery_details = []
        for t in delivery_tuples:
            temp_dict = {"del_address":t[0],"del_time":t[1]}
            delivery_details.append(temp_dict)                
        print ("delivery_details ↓")    
        print(delivery_details)
        
        # TODO: Clean up details in such a way that if that the pickup maps to the delivery and handle blank addresses
        # Use itertoolz 
        pickup_delivery_details_zipped = zip_longest(pickup_details, delivery_details, fillvalue="None")
        pickup_delivery_details = list(pickup_delivery_details_zipped)    
        print("pickup_delivery_details ↓")
        print(pickup_delivery_details)     


        bol_html =  render_template("bill_of_lading.html", your_company_name=your_company_name,logo_path=logo_path,your_company_phone=your_company_phone, your_company_address=your_company_address, 
                            dispatcher_name=dispatcher_name,dispatcher_email=dispatcher_email,dispatcher_phone=dispatcher_phone,
                            run_date=run_date,dock=dock,to_company=to_company,bill_to=bill_to,quantity=quantity,weight=weight,rate=rate,equipment_details=equipment_details,
                            pickup_delivery_details=pickup_delivery_details,comments=comments_formatted,
                            )

        bol_pdf = io.BytesIO()
        pisa.CreatePDF(bol_html, dest=bol_pdf)
        bol_pdf.seek(0)
        # pdf_response.headers['Content-Type'] = 'application/pdf'
        # pdf_response.headers['Content-Disposition'] = 'inline; filename=bill_of_lading.pdf'

        return send_file(bol_pdf, as_attachment=False, download_name='bill_of_lading.pdf')
        #return pdf_response
        #return bol_html

        # Emptying out the logos directory       
        # List of files in directory
        files_in_logos = os.listdir(logos_path)

        # loop through each file in the directory and delete it
        for file in files_in_logos:
            file_path = os.path.join(logos_path, file)
            os.remove(file_path)

    elif request.method == "GET":
        return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)