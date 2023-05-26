# Bill of Lading Generator

from models.imports import logging, Flask, flash, render_template, redirect, request, \
session, make_response, send_file, url_for, flash, send_from_directory, \
current_app, UserMixin, login_user, LoginManager, login_required, \
current_user, logout_user, Session, SQLAlchemy, ForeignKey, relationship, \
declarative_base, pisa, datetime, os, io, zip_longest, secure_filename, \
generate_password_hash, check_password_hash, FlaskForm, StringField, \
PasswordField, SubmitField, DataRequired, Regexp, Email, Length, \
secure_filename, Migrate, uuid, DebugToolbarExtension, clean, \
    Environment, Mail, Message, jsonify, URLSafeTimedSerializer, SignatureExpired, \
        BadTimeSignature

from helpers import login_required, empty_logos_dir, render_sf_load_sheet
from routes import bp as routing_bp
#from stripe_routes import stripe_bp
from models.forms import LoginForm, RegisterForm
from models.database import db, Person, Companies, PersonToCompany, Feedback, Plan, Subscription, BolDocuments
#import paypalrestsdk
import logging
import json
#import stripe
#import creds 

#from sandbox import send_email

app = Flask(__name__)



app.debug = False
app.logger.setLevel(logging.INFO)
# app.config["TEMPLATES_AUTO_RELOAD"] = True
app.register_blueprint(routing_bp)
#app.register_blueprint(stripe_bp)

UPLOAD_FOLDER = 'logos/'

# Mail configuration
# app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
# app.config["MAIL_PORT"] = 25
# app.config["MAIL_USE_TLS"] = False
# app.config["MAIL_USE_SSL"] = True
# app.config["MAIL_DEBUG"] = app.debug
# app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
# app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
# app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")
# app.config["MAIL_MAX_EMAILS"] = None
# app.config["MAIL_SUPPRESS_SEND"] = app.testing
# app.config["MAIL_ASCII_ATTACHMENTS"] = False
# mail = Mail(app)
app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.environ.get("MAIL_PORT"))
app.config['MAIL_USE_TLS'] = (os.environ.get("MAIL_USE_TLS")).lower() == 'true'
app.config['MAIL_USE_SSL'] = (os.environ.get("MAIL_USE_SSL")).lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_DEBUG'] = (os.environ.get("MAIL_DEBUG")).lower() == 'true'
app.config['MAIL_SUPPRESS_SEND'] = (os.environ.get("MAIL_SUPPRESS_SEND")).lower() == 'true'
app.config['MAIL_DEFAULT_SENDER'] = ("ShipFlow.xyz", "info@shipflow.xyz")
mail = Mail(app)

# Flask flask messages config
app.config['FLASH_MESSAGES_OPTIONS'] = {'timeout': 3}
app.config["SESSION_FILE_DIR"] = os.environ.get("SESSION_FILE_DIR")

# SQL Alchemy config
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initializing serializer
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Bind the db object from databse.py to this Flask application
db.init_app(app)
migrate = Migrate(app, db)

toolbar = DebugToolbarExtension(app)

# This clears the debugging toolbar and re-initializes it if uncommented
# toolbar = DebugToolbarExtension()
# # Then later on.
# app = create_app('the-config.cfg')
# toolbar.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Testing bluprint registration
for rule in app.url_map.iter_rules():
    print("route --> " + str(rule))

# # Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# app.config["USE_SESSION_FOR_NEXT"] = True
# Session(app)


@login_manager.user_loader
def load_user(user_id):
    return Person.query.get(int(user_id))

  
#Line below only required once, when creating DB. 
#db.create_all()
with app.app_context():    
    #send_email()
    db.create_all()
    print("executed in context")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"

    empty_logos_dir()
    # TODO: Send mail on after request
    # msg = Message("You have created a bill of lading pdf", sender="thatkalel@gmail.com",
    # recipients=["thatkalel@gmail.com"])
    # mail.send(msg)

    return response


@app.route("/")
def index():
    login_form = LoginForm()  
    print(current_user)    
    #print(current_user.stripe_customer_id)
    return render_template('index.html')


@app.route("/subscribe", methods = ['GET', 'POST'])
@login_required
def subscribe():
    print("Subscribe Request triggered")
    return ""
    # return render_template("subscribe.html")


@app.route("/login", methods = ['GET', 'POST'])
def login(): 
    login_form = LoginForm() 
    if request.method == "POST":       
        if login_form.validate_on_submit():
            if login_form.login.data:
                email = request.form.get("email")
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
                        print("current_user.id "+ str(current_user.id))
                        flash('Logged in successfully.', "success")
                        print("? user.is_authenticated: " +str(user.is_authenticated))
                        return render_template("form.html", first_name=first_name)
                    else:
                        # Password mismatch. FLash("Invalid email or password")
                        flash("Invalid email or password", "warning")
                        return render_template("login.html",form=login_form)
                
                elif not user:
                    # No email in db. FLash("Invalid email or password")
                    flash('Invalid email or password.', "warning")
                    print("No person in DB with this email. Redirect to Registration")
                    # print("Print is_authenticated ")
                    # print(user.is_authenticated)
                    return render_template("login.html",form=login_form)
                print("Login Request triggered")

        else:
            flash("Unable to sign this user", "warning")
            print("Unable to sign this user")
            return render_template("login.html",form=login_form)

    else:
        # If method is GET
        if current_user.is_authenticated:
            return render_template("form.html")
        else:
            return render_template("login.html", form=LoginForm())

  
@app.route('/verify_email/<verify_token>')
def verify_email(verify_token):
  try:    
    email = s.loads(verify_token, salt='verify-email', max_age=300)
    # Verify the user with "email" as their email in the Database  
    if Person.query.filter_by(email=email).count() == 1:
        user_to_verify = Person.query.filter_by(email=email).first()
        print("found verification email in db. checking if it matches current user")
        print("matches current user") # Note if they use a different browser, it won't match. Consider not matching. Lookup best practices
        # Update db
        user_to_verify.is_verified = True
        db.session.commit()
        return render_template("notification_templates/email_verified.html")
    else:
        print("did not find verification email in db")

  except SignatureExpired:
    print("SignatureExpired")
    return "<h1>Signature expired.</h1> \n <input type='submit' name='resend'>Resend Email?</input>"
  except BadTimeSignature:
    print("BadTimeSignature")
    return "<h2>The url does not match. Try clicking on the link in the email you received.</h2> <h2>If you choose to copy and paste the link, make sure it does not include any spaces.</h2>"
  
  return url_for('index')


@app.route("/register", methods = ['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if request.method == "POST":
        if register_form.validate_on_submit():
            print("Register Request triggered")   
            # Get registration data
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            username = request.form.get("username")
            email = request.form.get("email").lower()
            # display_name = request.form.get("display_name")
            password_hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
            
            # SQL: write data into db
            # Set data
            person_update = Person(username=username, first_name=first_name,last_name=last_name,
                                email=email, password_hash=password_hash)
            
            # Checking database before registering
            # If user already exists
            if Person.query.filter_by(email=email).count() >0:
                print(first_name + " already exists")
                flash("Oops! "+ email + " already exists. If this is you, please log in.", "warning")            
                return render_template("register.html",form=register_form)
            # If new user. Registering
            elif Person.query.filter_by(email=email).count() == 0:
                print(Person.query.filter_by(email=email).count())
                flash("Welcome, " +first_name + ". You've signed up successfully. We've sent you an email. Please verify your email.", "success")
                print(first_name + " did not exist. Registering user")
                db.session.add(person_update)
                db.session.commit()
                user = person_update
                is_logged_in = login_user(user)                

                # Email Verification process
                token = s.dumps(email, salt='verify-email')
                link = url_for('verify_email', verify_token=token, _external=True)                
                print(link)
                # Email the link
                # # Create and send the verification email                
                try:
                    print(email)
                    print(app.config['MAIL_DEFAULT_SENDER'])
                    msg = Message('Email Verification', recipients=[email])
                    msg.html = render_template('email_templates/verification_email.html', verification_link=link)
                    msg.body = "Thank you for registering! \nPlease use the following link to verify your email address:\n\n" + link + "\n\nIf you did not register for an account, please ignore this email."
                    print(msg.body)
                    print("Msg body: "+str(msg.body))
                    mail.send(msg)
                    print ("Verification email sent")
                except Exception as e:
                    print("Email failed to send: "+ str(e))

                return render_template("form.html")
            
            else:
                flash("Unable to Register this user", "warning")
                print("Unable to Register this user")
                return render_template("register.html",form=register_form)

            
        

        else:
            flash("Unable to Register this user", "warning")
            print("Unable to Register this user")
            return render_template("register.html",form=register_form)

    else:
        return render_template("register.html",form=register_form)


@app.route("/logout", methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    print("Logout Request triggered")
    flash("Logged out successfully", "success")
    return render_template("login.html", form=LoginForm())


@app.route("/form", methods = ['GET', 'POST'])
@login_required
def form():
    print("Request triggered")       
    if request.method == "POST":  
          
        # Getting values from the form
        your_company_name = clean(str(request.form.get("your_company_name")))    
        your_company_address = clean(str(request.form.get("your_company_address")))
        your_company_phone = clean(str(request.form.get("your_company_phone")))
        dispatcher_name = clean(str(request.form.get("dispatcher_name")))
        dispatcher_email = clean(str(request.form.get("dispatcher_email")))
        dispatcher_phone = clean(str(request.form.get("dispatcher_phone")))
        run_date = clean(str(request.form.get("run_date")))
        dock = clean(str(request.form.get("dock")))
        po_number = clean(str(request.form.get("po_number")))
        carrier = clean(str(request.form.get("carrier")))
        bill_to = clean(str(request.form.get("bill_to")))        
        rate = clean(str(request.form.get("rate")))
        equipment_details = clean(str(request.form.get("equipment_details")))
        logo_ext = clean(str(request.form.get("logo_ext")), tags=[], attributes={}, protocols=['http', 'https'])
        print("clean url: " + logo_ext)
        
        # Lists
        def clean_list(y):
            return [clean(x) for x in y]
        pickup_companies = request.form.getlist("pickup_company")
        pickup_companies = clean_list(pickup_companies)
        pickup_contacts = request.form.getlist("pickup_contact")
        pickup_contacts = clean_list(pickup_contacts)
        pickup_locations = request.form.getlist("pickup_location")
        pickup_locations = clean_list(pickup_locations)
        pickup_times = request.form.getlist("pickup_time")
        pickup_times = clean_list(pickup_times)
        delivery_companies = request.form.getlist("delivery_company")
        delivery_companies = clean_list(delivery_companies)
        delivery_contacts = request.form.getlist("delivery_contact")
        delivery_contacts = clean_list(delivery_contacts)
        delivery_locations = request.form.getlist("delivery_location")
        delivery_locations = clean_list(delivery_locations)
        delivery_times = request.form.getlist("delivery_time")
        delivery_times = clean_list(delivery_times)
        quantity = request.form.getlist("quantity")
        quantity = clean_list(quantity)
        weight = request.form.getlist("weight")
        weight = clean_list(weight)
        comments = request.form.getlist("comments")
        comments = clean_list(comments)
        
        
        logo_size = None
        # Files
        try:
            # Attempting to save the logo file in the logos dir
            logo = request.files["logo"]
            filename_unformatted = secure_filename(logo.filename)
            app.logger.info("filename_unformatted: " + str(filename_unformatted))
            # Setting unique filenames
            filename = str(uuid.uuid1()) + "_" + filename_unformatted 
            app.logger.info("filename: "+ str(filename))
            logo_path = os.path.join(UPLOAD_FOLDER, filename)
            app.logger.info(logo_path)
            if logo is not None:
                logo.save(logo_path)
                app.logger.info(logo_path) 
                logo_size = os.path.getsize(logo_path)
                app.logger.info(f"The size of {logo_path} is {logo_size} bytes.")
            else:
                app.logger.info("Not a valid file")
        except FileNotFoundError:
            print("Error getting logo. Caught FileNotFoundError")
        except IsADirectoryError:
            print("Did not upload a file. Caught isADirectoryError")        
             
        comments_formatted =  [x for x in comments if x != '']
        print(comments_formatted)        

        # Create a new list of dictionaries {"Address":value, "Time":value} for pickup locations
        pickup_tuples = list(zip_longest(pickup_companies, pickup_contacts, pickup_locations, pickup_times, fillvalue="None"))
        delivery_tuples =list(zip_longest(delivery_companies, delivery_contacts, delivery_locations, delivery_times, fillvalue="None"))
        qty_wgt_tuples = list(zip_longest(quantity, weight))


        # Create a list of dictionaries with pu_address and pu_time
        pickup_details =[]
        for t in pickup_tuples:
            temp_dict = {"pu_company":t[0],"pu_contact":t[1],"pu_address":t[2],"pu_time":t[3]}
            pickup_details.append(temp_dict)    
        print ("pickup_details ↓")       
        print(pickup_details)
        
        # Create a new list of dictionaries {"Address":value, "Time":value} foe delivery locations
        delivery_details = []
        for t in delivery_tuples:
            temp_dict = {"del_company":t[0],"del_contact":t[1],"del_address":t[2],"del_time":t[3]}
            delivery_details.append(temp_dict)                
        print ("delivery_details ↓")    
        print(delivery_details)

        # Create a new list of dictionaries {"Quantity":value}
        qty_wgt_details = []
        for t in qty_wgt_tuples:
            temp_dict = {"quantity":t[0], "weight": t[1]}
            qty_wgt_details.append(temp_dict)                
        print ("qty_wgt_details ↓")    
        print(qty_wgt_details)

        
        # Use itertoolz 
        pickup_delivery_details_zipped = zip_longest(pickup_details, delivery_details, qty_wgt_details, fillvalue="None")
        pickup_delivery_details = list(pickup_delivery_details_zipped)    
        print("pickup_delivery_details ↓")
        print(pickup_delivery_details)

        # Create document in DB
       
        

        is_sharing = False
        
        # TODO: 
        # if sharing:
            # ask for guest's email
            # search db for guest to get guest_id            
            # warn host about privacy and search db for email and
            # save to database with host_id and guest_id
            
            # send email to the guest
            # when guest opens, a form is recreated and updates the record when done
            # same thing happens with the host until host marks the record as complete
           

        # else:
            # render pdf as usual

        if request.form['action'] == "share":  
            guest_email = clean(str(request.form.get("guest_email")))
            print(guest_email)

            guest = Person.query.filter_by(email=guest_email).first()
            print("Guest -->  "+ str(guest))

            if guest:
                session_document = BolDocuments(host_id=current_user.id,guest_id=guest.id,broker_company_name=your_company_name,
                    broker_company_address=your_company_address,broker_company_phone=your_company_phone,
                    dispatcher_name=dispatcher_name,dispatcher_email=dispatcher_email,dispatcher_phone=dispatcher_phone,
                    carrier_company_name=carrier,equipment_details=equipment_details,bill_to=bill_to,po_number=po_number,
                    dock_number=dock,rate=rate,run_date=run_date,pickup_delivery_details=json.dumps(pickup_delivery_details),
                    comments=json.dumps(comments_formatted))

                db.session.add(session_document)
                db.session.commit()
                print(session_document.id) # works, returns the record object
                return "Should redirect to your portal page" # redirect to portal

            else:
                return "Unable to find the user with this email. Please check for spelling mistakes and verify with the user."

        else:        
            bol_html =  render_template("bill_of_lading.html", your_company_name=your_company_name,logo_path=logo_path,your_company_phone=your_company_phone, your_company_address=your_company_address, 
                                dispatcher_name=dispatcher_name,dispatcher_email=dispatcher_email,dispatcher_phone=dispatcher_phone,
                                run_date=run_date,dock=dock,carrier=carrier,bill_to=bill_to,rate=rate,equipment_details=equipment_details,
                                pickup_delivery_details=pickup_delivery_details,comments=comments_formatted,po_number=po_number,
                                logo_ext=logo_ext,logo_size=logo_size)

            sf_load_sheet = render_sf_load_sheet(bol_html)
            return sf_load_sheet


    elif request.method == "GET":
        if current_user.is_authenticated:
            return render_template("form.html")
        else:
            return render_template("login.html", form=LoginForm())



if __name__ == '__main__':
    app.run(debug=True)
