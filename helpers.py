from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, request
from models.imports import Environment, io, pisa, send_file, datetime
from models.database import Subscriptions
import os
import stripe

UPLOAD_FOLDER = 'logos/'


print("Helpers imported")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def empty_logos_dir():
    # Emptying out the logos directory       
    # List of files in directory    
    try:      
        files_list = os.listdir(UPLOAD_FOLDER)
        print("Emptying out the logos folder -> " + str(files_list))

        # loop through each file in the directory and delete it
        if len(files_list) != 0:
            for file in files_list:
                file_path = os.path.join(UPLOAD_FOLDER, file)
                os.remove(file_path)
    except FileNotFoundError:
        print("FileNotFoundError occured - possible empty logos directory")

def is_still_on_trial():
    if current_user.is_authenticated:
        current_datetime = datetime.now()
        join_date = current_user.created_at
        elapsed_days = (current_datetime - join_date).days
        print("Elapsed_days")
        if elapsed_days <= 14:
            print(f"Elapsed_days -- {elapsed_days}, On Trial")
            return True
        else:
            print(f"Elapsed_days -- {elapsed_days}, Trial Over")            
            return False
    else:
        return None


def check_sub_status():
    if current_user.is_authenticated:
        if current_user.id == 27:
            return "active"
        if current_user.stripe_customer_id:
            # Allowint for trial mode
            if is_still_on_trial() == True:
                return "active"
            # Get the curent expiration of this sub cycle
            subscription = Subscriptions.query.filter_by(stripe_customer_id=current_user.stripe_customer_id).first()
            if not subscription:
                return None
            subscription_id = subscription.subscription_id
            subscription_obj = stripe.Subscription.retrieve(subscription_id)

            # Check if we have crossed it
            current_period_end = datetime.fromtimestamp(subscription_obj.current_period_end)
            current_datetime = datetime.now()
            if current_datetime.date() >= current_period_end.date():
                print("Sub cycle expiry. Making stripe call and updating records") 
                try:
                    subscription = Subscription(
                            plan_id=plan_id,
                            subscription_id=subscription_id,
                            status=subscription_obj.status,
                            stripe_customer_id=stripe_customer_id,
                            start_date = datetime.fromtimestamp(subscription_obj.start_date),
                            current_period_end = current_period_end                       
                        )
                    db.session.add(subscription)
                    db.session.commit()
                    print("Subscription updated in check_sub_status")
                except Exception as e:
                        print("Could not update subscription in check_sub_status: ", e)
                               
            elif current_datetime.date() <= current_period_end.date():
                print("Sub end cycle has no approached. Not making stripe call")
                
            print(current_user.stripe_customer_id)
            sub = Subscriptions.query.filter_by(stripe_customer_id=current_user.stripe_customer_id).first()
            return sub.status
        else:
            return None
    else:
        return None


def render_sf_load_sheet(bol_html):
    bol_pdf = io.BytesIO()
    pisa.CreatePDF(bol_html, dest=bol_pdf)
    bol_pdf.seek(0)       

    return send_file(bol_pdf, as_attachment=False, download_name='bill_of_lading.pdf')
    #return bol_html