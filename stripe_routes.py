import importlib
import stripe
from helpers import login_required
from models.imports import Blueprint, render_template, request, current_app, \
    current_user, Session, SQLAlchemy, ForeignKey, relationship, \
declarative_base, pisa, datetime, os, io, zip_longest, secure_filename, \
generate_password_hash, check_password_hash, FlaskForm, StringField, \
PasswordField, SubmitField, DataRequired, Regexp, Email, Length, \
secure_filename, Migrate, uuid, DebugToolbarExtension, clean, \
    Environment, Mail, Message, jsonify
from models.database import db, Person, Companies, PersonToCompany, Feedback, Plan, Subscription


stripe_bp = Blueprint("stripe_r", __name__)


# This is your test secret API key.
YOUR_DOMAIN = "http://127.0.0.1:5000"
stripe.api_key = os.environ.get("stripe_api_key")
endpoint_secret = os.environ.get("endpoint_secret")

@stripe_bp.route("/checkout", methods=['GET'])
def checkout():
    print(stripe.api_key)
    print(endpoint_secret)
    return render_template("/checkout.html")

@stripe_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        prices = stripe.Price.list(
            lookup_keys=[request.form['lookup_key']],
            expand=['data.product']
        )

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                },
            ],
            metadata=
                { # Use to link shipflow user to stripe checkout session
                    "user_id": current_user.id
                }
            ,
            mode='subscription',
            success_url=YOUR_DOMAIN +
            '/success.html?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return "Server error", 500


def create_stripe_customer():
    # Creates stripe customer if sf does not have a stripe customer id
    sf_user = Person.query.filter_by(id=current_user.id).first()
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=sf_user.email,
            description="Test customer",
            metadata={
                'sf_user_id': str(current_user.id),
            }
        )
        # Updating shipflow db with stripe's customer id        
        sf_user.stripe_customer_id = customer.id
        db.session.commit()
    return sf_user


@stripe_bp.route('/create-subscription', methods=['POST'])
def create_subscription():
    print("subscribe created triggered")
    # TODO: Check stripe customers for sf_user_id before creating
    
    # TODO: REVISIT and check that sf_user and current_user always match
    sf_user = create_stripe_customer()
    #TODO: Find a way to check for an existing subscription of the 
    # same type before proceeding
    # Create a subscription for the user
    subscription = stripe.Subscription.create(
        customer=sf_user.stripe_customer_id,
        items=[{
            'price': "price_1N5GglASQh21FKPFawfnjrL1"
        }],
        metadata={
            'sf_user_id': str(current_user.id)
        }
    )
    print("Subscription id: " + str(subscription.id))
    # Save the subscription ID to the user's database record
    #sf_user.subscription_id = subscription.id
    #db.session.commit()

    return jsonify({'success': True})


@stripe_bp.route('/create-portal-session', methods=['POST'])
def customer_portal():
    # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
    # Typically this is stored alongside the authenticated user in your database.
    checkout_session_id = request.form.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = YOUR_DOMAIN

    portalSession = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=return_url,
    )
    return redirect(portalSession.url, code=303)


@stripe_bp.route('/stripe_webhooks', methods=['POST'])
def webhook():
    print("Webhook Triggered")
    #TODO: Use webhook secret before sensitive execution
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    #print(payload)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    print("Event below")
    print(event.type)
    #event_dict = json.loads(event)
    if ("metadata" in event.data.object):
        print(event.data.object.metadata)
    # # Handle the event
    # if event['type'] == 'payment_intent.succeeded':
    #   payment_intent = event['data']['object']
    # # ... handle other event types
    # # Handle the event
    # elif event['type'] == 'customer.subscription.created':
    #   subscription = event['data']['object']
    #   # Use to link shipflow user to stripe checkout session
    #   metadata = event['data']['object']['metadata']
    #   print(metadata)
    # # ... handle other event types
    # # ... handle other event types
    # else:
    #   print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)
        