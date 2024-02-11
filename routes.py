import importlib
import os
#import creds
from helpers import login_required
from models.imports import Blueprint, render_template, request, redirect, current_app, \
    current_user, URLSafeTimedSerializer, SignatureExpired, \
        BadTimeSignature, BadSignature, url_for, flash, Message, Mail, generate_password_hash
from models.database import db, Companies, Feedback, BolDocuments, Users


bp = Blueprint("routes_r", __name__)

# Initializions
s = URLSafeTimedSerializer(os.environ.get("SECRET_KEY"))
mail = Mail()


@bp.route("/feedback", methods = ['GET', 'POST'])
@login_required
def feedback():
    from models.forms import FeedbackForm, LoginForm
    feedback_form = FeedbackForm()
    if request.method == "POST":
        company_name = request.form.get("company_name")
        role = request.form.get("role")
        feedback = request.form.get("feedback")
        rating = request.form.get("rating")
        suggestions = request.form.get("suggestions")
        bug_reports = request.form.get("bug_reports")
        more_comments = request.form.get("more_comments")
        person_id = current_user.id
        print(person_id)
        print(request.form)
        print("Feedback Request triggered")

        # TODO: Revise. There will be duplicates
        result = Companies.query.filter_by(company_name=company_name).first()
        if result:
            company_id = result.id
        else:
            company_id = None
        print("company_id: "+str(company_id))
       
        feedback_update = Feedback(person_id=person_id, company_name=company_name,
                            role=role,feedback=feedback,rating=rating, suggestions=suggestions,bug_reports=bug_reports,
                            more_comments=more_comments,company_id=company_id)

        db.session.add(feedback_update)
        db.session.commit()

        # TODO: Return a thank you for your feedback form
        return render_template("feedback.html", form=feedback_form)
    
    else:
        if current_user.is_authenticated:
            return render_template("feedback.html",form=feedback_form)
        else:
            return render_template("login.html", form=LoginForm())


@bp.route("/portal", methods = ['GET', 'POST'])
def portal():
    from models.forms import RecordForm
    record_form = RecordForm()
    if request.method == 'POST':
        return "Initiate Update record"
    
    elif request.method == 'GET':
        # Create a list of host and guest records
        host_records = BolDocuments.query.filter_by(host_id=current_user.id).all()
        guest_records = BolDocuments.query.filter_by(guest_id=current_user.id).all()
        print("host below")
        print(host_records)
        print ("guest below")
        print(guest_records)
        
        # Creates a list of forms with the data from each from the host_records list
        host_forms = [RecordForm(obj=host_record) for host_record in host_records]
        guest_forms = [RecordForm(obj=guest_record) for guest_record in guest_records]
        # Create a list of guest records

        return render_template("portal.html", form=record_form, host_forms=host_forms, 
            guest_forms=guest_forms)


@bp.route("/error/<error_type>")
def error(error_type):
    return render_template("error.html", error_type=error_type)


@bp.route("/profile", methods=['GET', 'POST'])
def profile():
    from models.forms import ProfileForm, PasswordResetForm
    if current_user.is_authenticated:
        profile = Users.query.filter_by(id=current_user.id).first() 
        profile_form = ProfileForm(obj=profile)

        if profile_form.validate_on_submit(): 
            # If reset password is clicked
            if profile_form.reset_password_button.data:
                print("Reset password was clicked")
                password_reset_form = PasswordResetForm()
                reset_token = s.dumps(current_user.email, salt='change-password')                  
                return redirect(url_for("routes_r.reset_password", reset_token=reset_token, form=password_reset_form))
            elif profile_form.update.data:
                # TODO: Update data that was changed and that are allowed 
                # to be changed by the user, then re-render page
                return render_template("notification_templates/upcoming_feature.html")
                #return render_template("profile.html", form=profile_form)                
        else:
            return render_template("profile.html", form=profile_form)
    else:
        flash("Please log in to proceed.")
        return redirect(url_for('index'))


@bp.route('/reset_password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):
    from models.forms import ProfileForm, PasswordResetForm
    password_reset_form = PasswordResetForm()
    if request.method == 'GET':
        print("Reset GET method triggered")
        print(reset_token)
        if not reset_token:
            flash("An error occured. Please try again.")
            return redirect(url_for('routes_r.error', error_type="Invalid reset token"))
        else:
            print("Trying to print url")
            print(url_for('routes_r.reset_password', reset_token=reset_token))
            return render_template("password/password_reset.html", reset_token=reset_token, form=password_reset_form)

    elif request.method == 'POST'and password_reset_form.validate_on_submit():
        print("reset token passed: " + str(reset_token))
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        try:    
            salts=['change-password', 'forgot-password']
            reset_type = None
            check_email = None
            for salt in salts:
                try:
                    check_email = s.loads(reset_token, salt=salt, max_age=3000)
                except BadSignature:
                    continue
                except SignatureExpired:  
                    continue
                else:
                    reset_type=salt
                    print(reset_type)            
            
            # Verify the user with "email" as their email in the Database  
            if Users.query.filter_by(email=check_email).count() == 1:
                update_user = Users.query.filter_by(email=check_email).first()
                print("found password change user in db. checking if it matches current user")
                if reset_type == "change-password":
                    if current_user == update_user:
                        print("matches current user")
                        print("Should update password here")
                        # TODO: Update db with new password hash 
                        print("change password situation")                   
                        # Redundant check for password match, hash and update
                        if new_password == confirm_password:
                            password = new_password
                            password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                            update_user.password_hash = password_hash
                            db.session.commit()
                            return render_template("notification_templates/password_updated.html")
                        else:
                            flash("Mismatch error.") 
                            return render_template("password_reset.html", reset_token=reset_token, form=password_reset_form)
                    else:
                        flash("Authentication error")
                        return redirect(url_for('routes_r.error', error_type="There was an authentication error."))
                else:
                    print("forgot password situation")
                    # Redundant check for password match, hash and update
                    if new_password == confirm_password:
                        password = new_password
                        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                        update_user.password_hash = password_hash
                        db.session.commit()
                        return render_template("notification_templates/password_updated.html")
                    else:
                        flash("Mismatch error.") 
                        return render_template("password/password_reset.html", reset_token=reset_token, form=password_reset_form)
            else:
                # DID not find user, Go to log in or register page
                print("did not find the user in db")
                flash("User not found. Please log in or register.")
                return redirect(url_for('register'))

        except SignatureExpired:
            print("SignatureExpired")
            flash("Signature expired. Try again or contact support if the issue persists.")
            return redirect(url_for('routes_r.error', error_type="Expired signature. You waited too long."))
        except BadTimeSignature:
            print("BadTimeSignature")
            flash("The URL does not match. Try clicking on the link in the email you received.")
            return redirect(url_for('routes_r.error', error_type="Bad time signarue."))

    else:
        flash("Invalid request. Please ensure the passwords match.")
        return render_template("password/password_reset.html", reset_token=reset_token, form=password_reset_form)
    

@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    from models.forms import ForgotPasswordForm
    forgot_password_form = ForgotPasswordForm()
    if forgot_password_form.validate_on_submit():
        email = request.form.get("email")
        # If the email is in our database
        if Users.query.filter_by(email=email).count() == 1:            
            reset_token = s.dumps(email, salt='forgot-password')
            reset_link = url_for('routes_r.reset_password', reset_token=reset_token, _external=True)
            print("reset_link: "+ str(reset_link))
            # TODO: Email reset_token link to the email 
            try:
                print(email)
                print(current_app.config['MAIL_DEFAULT_SENDER'])
                msg = Message('Password Reset', recipients=[email])
                msg.html = render_template('email_templates/forgot_password.html', reset_password_link=reset_link)
                msg.body = "Please click the link below to reset your password:\n\n" + reset_link + "\n\nIf you did not make this request, please ignore this email."
                print(msg.body)
                print("Msg body: "+str(msg.body))
                mail.send(msg)
                print ("Password reset email sent")
            except Exception as e:
                print("Email failed to send: "+ str(e))
                return redirect(url_for('routes_r.error', error_type=e))
            else:
                # TODO: fix below, render proper
                return "Reset email sent"
        else:
            flash("Invalid entry")
            return render_template("password/request_password_reset.html", form=forgot_password_form)
    else:
        return render_template("password/request_password_reset.html", form=forgot_password_form)


