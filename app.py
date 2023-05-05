# Bill of Lading Generator

from models.imports import Flask, flash, render_template, redirect, request, \
session, make_response, send_file, url_for, flash, send_from_directory, \
current_app, UserMixin, login_user, LoginManager, login_required, \
current_user, logout_user, Session, SQLAlchemy, ForeignKey, relationship, \
declarative_base, pisa, datetime, os, io, zip_longest, secure_filename, \
generate_password_hash, check_password_hash, FlaskForm, StringField, \
PasswordField, SubmitField, DataRequired, Regexp, Email, Length, \
secure_filename, Migrate, uuid, DebugToolbarExtension, clean, \
    Environment

from helpers import login_required
from routes import bp as routing_bp
from models.forms import LoginForm, RegisterForm
from models.database import db, Person, Companies, PersonToCompany, Feedback
#import creds 


app = Flask(__name__)

app.debug = False
# app.config["TEMPLATES_AUTO_RELOAD"] = True
app.register_blueprint(routing_bp)

app.config['FLASH_MESSAGES_OPTIONS'] = {'timeout': 3}
app.config["SESSION_FILE_DIR"] = os.environ.get("SESSION_FILE_DIR")

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'logos/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




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
    login_form = LoginForm()  
    # print(current_user)    
    if current_user.is_authenticated:
        return render_template("form.html")
    else:
        return render_template("login.html", form=login_form)


@app.route("/subscribe", methods = ['GET', 'POST'])
@login_required
def subscribe():
    print("Subscribe Request triggered")
    return render_template("subscribe.html")


@app.route("/login", methods = ['GET', 'POST'])
def login(): 
    login_form = LoginForm() 
    if request.method == "POST":        
        if login_form.validate_on_submit():
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
            #print(password_hash)

            # SQL: write data into db
            # Set data
            person_update = Person(username=username, first_name=first_name,last_name=last_name,
                                email=email, password_hash=password_hash)
            
            # Checking database before registering
            if Person.query.filter_by(email=email).count() >0:
                print(first_name + " already exists")
                flash("Oops! "+ email + " already exists. If this is you, please log in.", "warning")            
                return render_template("register.html",form=register_form)

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
        to_company = clean(str(request.form.get("to_company")))
        bill_to = clean(str(request.form.get("bill_to")))
        quantity = clean(str(request.form.get("quantity")))
        weight = clean(str(request.form.get("weight")))
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
        comments = request.form.getlist("comments")
        comments = clean_list(comments)
        
        
        logo_size = None
        # Files
        try:
            # Attempting to save the logo file in the logos dir
            logo = request.files["logo"]
            filename_unformatted = secure_filename(logo.filename)
            print("filename_unformatted: " + str(filename_unformatted))
            # Setting unique filenames
            filename = str(uuid.uuid1()) + "_" + filename_unformatted 
            print("filename: "+ str(filename))
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(logo_path)
            logo.save(logo_path)
            print(logo_path) 
            logo_size = os.path.getsize(logo_path)
            print(f"The size of {logo_path} is {logo_size} bytes.")
        except FileNotFoundError:
            print("Error getting logo. Caught FileNotFoundError")
        except IsADirectoryError:
            print("Did not upload a file. Caught isADirectoryError")        
             
        comments_formatted =  [x for x in comments if x != '']
        print(comments_formatted)        

        # Create a new list of dictionaries {"Address":value, "Time":value} for pickup locations
        pickup_tuples = list(zip_longest(pickup_companies, pickup_contacts, pickup_locations, pickup_times, fillvalue="None"))
        delivery_tuples =list(zip_longest(delivery_companies, delivery_contacts, delivery_locations, delivery_times, fillvalue="None"))
      
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
        
        # TODO: Clean up details in such a way that if that the pickup maps to the delivery and handle blank addresses
        # Use itertoolz 
        pickup_delivery_details_zipped = zip_longest(pickup_details, delivery_details, fillvalue="None")
        pickup_delivery_details = list(pickup_delivery_details_zipped)    
        print("pickup_delivery_details ↓")
        print(pickup_delivery_details)     


        bol_html =  render_template("bill_of_lading.html", your_company_name=your_company_name,logo_path=logo_path,your_company_phone=your_company_phone, your_company_address=your_company_address, 
                            dispatcher_name=dispatcher_name,dispatcher_email=dispatcher_email,dispatcher_phone=dispatcher_phone,
                            run_date=run_date,dock=dock,to_company=to_company,bill_to=bill_to,quantity=quantity,weight=weight,rate=rate,equipment_details=equipment_details,
                            pickup_delivery_details=pickup_delivery_details,comments=comments_formatted,po_number=po_number,
                            logo_ext=logo_ext,logo_size=logo_size)

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
        if current_user.is_authenticated:
            return render_template("form.html")
        else:
            return render_template("login.html", form=LoginForm())

if __name__ == '__main__':
    app.run(debug=True)