import importlib
import stripe
from helpers import login_required
from models.imports import Blueprint, render_template,redirect, request, current_app, \
    current_user, Session, SQLAlchemy, ForeignKey, relationship, \
declarative_base, pisa, datetime, os, io, zip_longest, secure_filename, \
generate_password_hash, check_password_hash, FlaskForm, StringField, \
PasswordField, SubmitField, DataRequired, Regexp, Email, Length, \
secure_filename, Migrate, uuid, DebugToolbarExtension, clean, \
    Environment, Mail, Message, jsonify, exc, traceback, declarative_base
from models.database import db, Person, Companies, PersonToCompany, Feedback, \
     Plan, Subscription, Idempotent_Request, Webhook_Response

stripe_bp = Blueprint("stripe_r", __name__)

Base = declarative_base()

# This is your test secret API key.
YOUR_DOMAIN = "http://shipflow.xyz"
#YOUR_DOMAIN = "http://127.0.0.1:5000"
stripe.api_key = os.environ.get("stripe_api_key")
endpoint_secret = os.environ.get("endpoint_secret")


@stripe_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    print("IN create-checkout-session")
    try:
        idempotency_key= "sf_idp_key_"+str(uuid.uuid1())
        #Create a stripe customer if one does not exist for this use
        #  and use the stripe customer for this user if one exists
        if not current_user.stripe_customer_id:
            # Create customer since one does not exist
            customer = stripe.Customer.create(
                name=current_user.first_name+" "+current_user.last_name,
                metadata={"sf_user_id": current_user.id},
                idempotency_key=idempotency_key
            ) 
            # Initialize stripe_customer_id for the rest of the function
            stripe_customer_id = customer.id
            # Update the customer info serverside
            current_user.stripe_customer_id = stripe_customer_id

            # Create idempotency table entry
            add_idp_key = Idempotent_Request(
                idempotency_key=idempotency_key,
                sf_user_id=current_user.id,
                generated_in="create-checkout-session",
                generated_by="stripe.Customer.create"
            )

            db.session.add(add_idp_key)            
            db.session.commit()
            print("There was no stripe id for the customer, created customer: ", customer)
            print(current_user)

        else:
            stripe_customer_id = current_user.stripe_customer_id

        if current_user.stripe_customer_id:
            prices = stripe.Price.list(
                lookup_keys=[request.form['lookup_key']],
                expand=['data.product']
                )

            if not prices.data:  # Check if prices list is empty
                return "Invalid lookup key", 400

            # Creating the checkout session
            checkout_session = stripe.checkout.Session.create(
                customer = stripe_customer_id,
                line_items=[
                    {
                        'price': prices.data[0].id,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                client_reference_id=str(current_user.id),
                success_url=YOUR_DOMAIN +
                '/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=YOUR_DOMAIN + '/cancel'
            )
            print("Created session")         

            return redirect(checkout_session.url, code=303)
        
        else:
            return "Server error", 500
            
    except Exception as e:
        #traceback.print_exc()
        print("Error in checkout session: "+ str(e))
        return "Server error", 500


@stripe_bp.route('/create-portal-session', methods=['POST'])
@login_required
def customer_portal():
    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = YOUR_DOMAIN + '/profile.html'
    if current_user.stripe_customer_id:
        portalSession = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=return_url,
        )
        return redirect(portalSession.url, code=303)
    else:
        return "User not authenticated or subscribed"

# ----- WEBHOOKS
@stripe_bp.route('/stripe_webhooks', methods=['POST'])
@login_required
def webhook():
    print("Webhook Triggered")
    event = None
    idempotency_key= None
    idempotency_key_id = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    try:
        event = stripe.Webhook.construct_event(payload, sig_header,
                                               endpoint_secret)
        data = event['data']
        event_type = event['type']
        event_id = event['id']
        print("Event Type: " + event_type)
        print("Event ID: " + event_id)
        idempotency_key=event['request']['idempotency_key']
        if idempotency_key:            
            print("idempotency_key: "+ idempotency_key)
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Idempotency check
    def is_idempotent():
        pre_recorded_webhook = []
        try:
            # Check the idp table for this idempotency_key into idempotency_key_id
            print(f"is_idempotent() {event_type},  idempotency_key: {str(idempotency_key)}")
            idempotency_obj = Idempotent_Request.query.filter_by(idempotency_key=idempotency_key).first()
            
            if idempotency_obj:
                idempotency_key_id = idempotency_obj.id
            else:
                # No idempotency_key recorded. Therefore is idempotent. Return True
                print("No idempotency_key recorded. Therefore is idempotent. Return True")
                return True
            # Check webhook table for a previous recorded occurence of the current event
            pre_recorded_webhook = Webhook_Response.query.filter_by(idempotency_key_id=idempotency_key_id, evt_type=event_type).all()
        except Exception as e:
            # This should mean there is no current. Is idempotent
            print("Raised exception working with idempotency_key_id and/or pre_recorded_webhook indicating no previous recording of this idempotency key.  Returning True for is_idempotent")
            print(f"{event_type}, {event_id},  idempotency_key: {str(idempotency_key)} is idempotent. Error: {e}")
            return True
        # Idempotent webook count check
        if len(pre_recorded_webhook) == 0:
            print(f"Idempotent webook count check {event_type}, {event_id},  idempotency_key: {str(idempotency_key)} is idempotent")
            return True
        else:
            # Found previous occurrence 
            print(f"Found webhook record, {event_type}, {event_id},  idempotency_key: {str(idempotency_key)} is NOT idempotent")
            return False

    # --- EVENT TYPES    
    if event_type == 'checkout.session.completed':
        if is_idempotent() == True:
            # print("Printing event")
            # print(event)
            metadata = event.data.object.metadata
            print(metadata)
            print('🔔 Payment succeeded!')
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)

    # Charge failed
    elif event_type == 'charge.failed':
        if is_idempotent() == True:
            # print("Printing event")
            # print(event)
            print('Customer charge.failed')
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)

    # Charge succeeded
    elif event_type == 'charge.succeeded':
        print("Event Type: " + event_type)
        if is_idempotent() == True:
            # print("Printing event")
            # print(event)
            print('Customer charge.succeeded')
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)
               


    # CUSTOMER OBJECTS
    # Customer Created
    elif event_type == 'customer.created':
        print("Event Type: " + event_type)
        if is_idempotent() == True:
            stripe_customer_id = event.data.object.id
            print(stripe_customer_id)
                    
            sf_user_id = int(event.data.object.metadata.get("sf_user_id"))
            print("customer created metadata: "+ str(sf_user_id))
            if sf_user_id:
                sf_user = Person.query.get(sf_user_id)
                if sf_user:
                    print("Found corresponding user in customer created hook " +
                        str(sf_user))
                    if not sf_user.stripe_customer_id == stripe_customer_id:
                        print("LINK ERROR - MISMATCHED STRIPE TO SF ID")
                        # sf_user.stripe_customer_id = stripe_customer_id
                        # print("updating db")
                        # db.sessions.commit()
                    else:
                        print("The right stripe_customer_id already existed for the customer in the database")
                else:
                    print(
                        "Did not find corresponding user in the customer created hook"
                    )
            else:
                print("**** In customer created hook, did not get sf_user_metadata")
            
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)


    # Customer Deleted
    elif event_type == 'customer.deleted':
        print("Event Type: " + event_type)
        if is_idempotent() == True:
            stripe_customer_id = event.data.object.id
            
            sf_user = Person.query.filter_by(stripe_customer_id=stripe_customer_id).first()

            if sf_user:
                print("Found corresponding user in customer deleted hook " +
                        str(sf_user))
                
                sf_user.stripe_customer_id = None
                print("updating db -- removing stripe_customer_id from this user")
                db.session.commit()
            else:
                print("*** Did not find the customer to delete")
            
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)
    
    # SUBSCRIPTION OBJECT
    # Subscription created
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
        if is_idempotent() == True:
            try:
                subscription_obj = event.data.object
                subscription_id = subscription_obj.id
                stripe_plan_id = subscription_obj['items']['data'][0]['plan']['id']
                print("stripe_plan_id: ", stripe_plan_id)
                print("subscription_id: ", subscription_id)
                stripe_customer_id = subscription_obj.customer
                print("Event Type: " + event_type)
                # print("Printing event")
                # print(event)
                plan = Plan.query.filter_by(stripe_plan_id = stripe_plan_id).first()
                plan_id=None
                print("plan id init: ",plan_id)
                # Making sure to populate our plan table
                if plan:
                    print("in sub create stripe obj there is a current plan")
                    plan_id = plan.id
                else:
                    print("in sub create stripe obj NO current plan")
            
                    try:
                        add_plan = Plan(
                            stripe_plan_id=stripe_plan_id,
                            interval=subscription_obj['items']['data'][0]['plan']['interval'],
                            plan_name=subscription_obj['items']['data'][0]['plan']['nickname'],
                            price=subscription_obj['items']['data'][0]['plan']['amount']
                        ) 
                        db.session.add(add_plan)
                        db.session.commit()
                        print("Plan added successfully")
                    except Exception as e:
                        print("Error adding plan:", e)
                        db.session.rollback()
                    plan = Plan.query.filter_by(stripe_plan_id=stripe_plan_id).first()
                    plan_id = plan.id
                print("To use in create plan id: ",plan_id)
                
                # Populate the subscription table
                print("subscription_obj.start_date ->  ", str(subscription_obj.start_date))
                subscription = Subscription.query.filter_by(subscription_id=subscription_id).first()
                print("subscription check before creating in create evt")
                print(subscription)
                if not subscription:
                    # Create the sub if this hooks before the update hook
                    try:
                        subscription = Subscription(
                            plan_id=plan_id,
                            subscription_id=subscription_id,
                            status=subscription_obj.status,
                            stripe_customer_id=stripe_customer_id,
                            start_date = datetime.fromtimestamp(subscription_obj.start_date),
                            current_period_end = datetime.fromtimestamp(subscription_obj.current_period_end)
                        )
                        print("Creating in create evt " + str(subscription))
                        db.session.add(subscription)     
                        db.session.commit()
                    except Exception as e:
                        print("Did not create subscription in create event, should already exist: ", e)
                else:
                    # If it already exists, it was from the update hook, do nothing here
                    print("In sub create event, sub already exists")
            except Exception as e:
                print("****Error updating subscription created: ", e)
            
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)

    # Subscription updated
    elif event_type == 'customer.subscription.updated':
        print('Subscription updated %s', event.id)
        if is_idempotent() == True:
            try:
                subscription_obj = event.data.object
                subscription_id = subscription_obj.id
                stripe_plan_id = subscription_obj['items']['data'][0]['plan']['id']
                print("stripe_plan_id: ", stripe_plan_id)
                stripe_customer_id = subscription_obj.customer
                print("Event Type: " + event_type)
                # print("Printing event")
                # print(event)
                
                print("stripe_customer_id in subsc updated " + stripe_customer_id)
                plan = Plan.query.filter_by(stripe_plan_id = stripe_plan_id).first()
                print(plan)
                plan_id=None
                print("plan id init: ",plan_id)
                # Making sure to populate our plan table
                if plan:
                    print("in sub update stripe obj There is a current plan")
                    plan_id = plan.id
                    print(plan_id)
                else:
                    print("in sub update stripe obj NO current plan")
                    try:
                        add_plan = Plan(
                            stripe_plan_id=stripe_plan_id,
                            interval=subscription_obj['items']['data'][0]['plan']['interval'],
                            plan_name=subscription_obj['items']['data'][0]['plan']['nickname'],
                            price=subscription_obj['items']['data'][0]['plan']['amount']
                        ) 
                        db.session.add(add_plan)
                        db.session.commit()
                        print("Plan added successfully")
                    except Exception as e:
                        print("Error adding plan:", e)
                        db.session.rollback()
                    plan = Plan.query.filter_by(stripe_plan_id = stripe_plan_id).first()
                    plan_id = plan.id
                    print(plan_id)
                
                print("To use in update plan id: ",plan_id)
                print("subscription_id ->  ", subscription_id)
                print("subscription_obj.start_date ->  ", str(subscription_obj.start_date))                
                print("subscription_obj.current_period_end ->  ", str(subscription_obj.current_period_end))                
                print("subscription_obj.status ->  ", str(subscription_obj.status))
                
                
                subscription = Subscription.query.filter_by(subscription_id=subscription_id).first()
                print("subscription check before creating in update evt")
                print(subscription)
                if not subscription:
                    # Creates the subscription if it doesn't exist at this stage
                    try:
                        subscription = Subscription(
                            plan_id=plan_id,
                            subscription_id=subscription_id,
                            status=subscription_obj.status,
                            stripe_customer_id=stripe_customer_id,
                            start_date = datetime.fromtimestamp(subscription_obj.start_date),
                            current_period_end = datetime.fromtimestamp(subscription_obj.current_period_end)                            
                        )
                        print("Creating in update stage " + str(subscription))
                        db.session.add(subscription)
                        db.session.commit()
                        print('Subscription created %s', event.id)
                    except Exception as e:
                        print("Did not create subscription in update event, should already exist: ", e)
                
                else:
                    # Update the sub if it exists
                    print("subscription db query")
                    print(subscription)
                    subscription.status = subscription_obj.status
                    subscription.plan_id = plan_id
                    subscription.current_period_end = datetime.fromtimestamp(subscription_obj.current_period_end)
                    print("Updating " + str(subscription))
                    db.session.add(subscription)
                    db.session.commit()
                
            except Exception as e:
                print("**** Error updating subscription updated: ", e)
            
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)
            # Other situations where the subscription is just updated by itself
            subscription = Subscription.query.filter_by(subscription_id=subscription_id).first()
            if subscription:
                subscription.status = subscription_obj.status
                db.session.add(subscription)
                db.session.commit()

    # Subscription Deleted
    elif event_type == 'customer.subscription.deleted':        
        try:
            subscription_id = event.data.object.id
            print("Event Type: " + event_type)                                
            subscription = Subscription.query.filter_by(subscription_id=subscription_id).first()                
            print(f"in sub deleting, updating db status to {subscription_obj.status}: {str(subscription)}")
            subscription.status = subscription_obj.status
            db.session.add(subscription)

            # handle subscription canceled automatically based
            # upon your subscription settings. Or if the user cancels it.
            print('Subscription canceled: %s', event.id)
        except Exception as e:
            print("**** Error updating subscription: deleted ", e)
        
        # Create the record for first time occurence webhook table            
        add_wh_record = Webhook_Response(
            idempotency_key_id=idempotency_key_id,
            evt_type=event_type,
            evt_id=event_id
        )            
        db.session.add(add_wh_record)
        db.session.commit()
        

    # Subscription Paused
    elif event_type == 'customer.subscription.paused':
        try:
            subscription_obj = event.data.object
            subscription_id = event.data.object.id
            print("Event Type: " + event_type)                    
            subscription = Subscription.query.filter_by(
                subscription_id=subscription_id).first()
            print(f"in sub paused, updating db status to {subscription_obj.status}: {str(subscription)}")
            subscription.status = subscription_obj.status
            db.session.add(subscription)
            print('Subscription paused %s', event.id)
        except Exception as e:
            print("**** Error updating subscription paused: ", e)

        # Create the record for first time occurence webhook table            
        add_wh_record = Webhook_Response(
            idempotency_key_id=idempotency_key_id,
            evt_type=event_type,
            evt_id=event_id
        )            
        db.session.add(add_wh_record)
        db.session.commit()

    # Subscription Resumed
    elif event_type == 'customer.subscription.resumed':
        try:
            subscription_obj = event.data.object
            subscription_id = event.data.object.id
            print("Event Type: " + event_type)
                        
            subscription = Subscription.query.filter_by(subscription_id=subscription_id).first()
            print(f"in sub resumed, updating db status to {subscription_obj.status}: {str(subscription)}")
            subscription.status = subscription_obj.status
            db.session.add(subscription)
            print('Subscription resumed %s', event.id)
        except Exception as e:
            print("**** Error updating subscription resumed: ", e) 

        # Create the record for first time occurence webhook table            
        add_wh_record = Webhook_Response(
            idempotency_key_id=idempotency_key_id,
            evt_type=event_type,
            evt_id=event_id
        )            
        db.session.add(add_wh_record)
        db.session.commit()
        

    elif event_type == 'invoice.created':
        #TODO: Send notifications
        print('Invoice handle: %s', event.id)
        if is_idempotent() == True:
            print("TODO: handle invoice event: "+ event_type)
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)

    elif event_type == 'invoice.payment_failed':
        #TODO: Send notifications
        print('Invoice handle %s', event.id)
        if is_idempotent() == True:
            print("TODO: handle invoice event: "+ event_type)
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)

    elif event_type == 'invoice.payment_succeeded':
        #TODO: Send notifications
        print('Invoice handle %s', event.id)
        if is_idempotent() == True:
            print("TODO: handle invoice event: "+ event_type)
            # Create the record for first time occurence webhook table            
            add_wh_record = Webhook_Response(
                idempotency_key_id=idempotency_key_id,
                evt_type=event_type,
                evt_id=event_id
            )            
            db.session.add(add_wh_record)
            db.session.commit()
        else:
            print("***Non idempotent block --- "+ event_type)

    return jsonify({'status': 'success'})
