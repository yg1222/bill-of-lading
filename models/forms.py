

from .imports import FlaskForm, StringField, PasswordField, PasswordField, \
    SubmitField, DataRequired, Regexp, Email, Length, TextAreaField, SelectField

# Login and register form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], 
    render_kw={"class": "form-control col-sm-4", "placeholder":"Email"}, )
    password = PasswordField('Password', validators=[DataRequired()], 
    render_kw={"class": "form-control col-sm-4", "placeholder":"Password"} )
    submit = SubmitField('Sign in', render_kw={"class":"btn sign-up"})

class RegisterForm(FlaskForm):    
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=50)],
    render_kw={"class": "form-control col-sm-4", "placeholder":"First Name"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=50)],
    render_kw={"class": "form-control col-sm-4", "placeholder":"Last Name"})    
    username = StringField('Username', validators=[DataRequired(), Regexp('^\S+$'), Length(min=3, max=20)],
    render_kw={"class": "form-control col-sm-4", "placeholder":"Username"})    
    email = StringField('Your Email', validators=[DataRequired(), Email()], 
    render_kw={"class": "form-control col-sm-4", "placeholder":"Email"}, )
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], 
    render_kw={"class": "form-control col-sm-4", "placeholder":"Password"} )
    submit = SubmitField('Sign up', render_kw={"class":"btn sign-up"})

class FeedbackForm(FlaskForm):    
    company_name = StringField('Company Name',
    render_kw={"class": "form-control col-sm-4", "placeholder":"Company Name"})
    
    role = StringField('Role',
    render_kw={"class": "form-control col-sm-4", "placeholder":"Role"})    
    
    feedback = TextAreaField('Feedback', validators=[DataRequired()],
    render_kw={"class": "form-control col-sm-4", "placeholder":"Feedback"})    
    
    rating = SelectField('Rating', 
    choices=[('5', '5 - Excellent'), ('4', '4 - Good'), 
    ('3', '3 - Fair'), ('2', '2 - Poor'), ('1', '1 - Very Poor')], 
    default='3', validators=[DataRequired()])

    suggestions = TextAreaField('Suggestions', validators=[DataRequired()], 
    render_kw={"class": "form-control col-sm-4", "placeholder":"Suggestions"} )
    
    bug_reports = TextAreaField('Bug Reports', 
    render_kw={"class": "form-control col-sm-4", "placeholder":"Bug reports if any"}, )
    
    more_comments = StringField('More Comments', 
    render_kw={"class": "form-control col-sm-4", "placeholder":"More comments"} )
    
    submit = SubmitField('Sumbit Feedback', render_kw={"class":"btn sign-up"})



class Profile(FlaskForm):    
    company_name = StringField('Company Name',
    render_kw={"class": "form-control col-sm-4", "placeholder":"Company Name"})
    
    role = StringField('Role',
    render_kw={"class": "form-control col-sm-4", "placeholder":"Role"})    
    
    feedback = TextAreaField('Feedback', validators=[DataRequired()],
    render_kw={"class": "form-control col-sm-4", "placeholder":"Feedback"})    
    
    rating = SelectField('Rating', 
    choices=[('5', '5 - Excellent'), ('4', '4 - Good'), 
    ('3', '3 - Fair'), ('2', '2 - Poor'), ('1', '1 - Very Poor')], 
    default='3', validators=[DataRequired()])

    suggestions = TextAreaField('Suggestions', validators=[DataRequired()], 
    render_kw={"class": "form-control col-sm-4", "placeholder":"Suggestions"} )
    
    bug_reports = TextAreaField('Bug Reports', 
    render_kw={"class": "form-control col-sm-4", "placeholder":"Bug reports if any"}, )
    
    more_comments = StringField('More Comments', 
    render_kw={"class": "form-control col-sm-4", "placeholder":"More comments"} )
    
    submit = SubmitField('Sumbit Feedback', render_kw={"class":"btn sign-up"})


class RecordForm(FlaskForm):    
    id = StringField('Document ID',
    render_kw={"class": "form-control col-sm-4"})
    
    host_id = StringField('Host ID',
    render_kw={"class": "form-control col-sm-4"})    
    
    guest_id = StringField('Guest ID',
    render_kw={"class": "form-control col-sm-4"})    
    
    broker_company_name = StringField('Broker / Company Name',
    render_kw={"class": "form-control col-sm-4"}) 

    broker_company_address = StringField('Broker / Company Address', 
    render_kw={"class": "form-control col-sm-4"})
    
    broker_company_phone = StringField('Broker / Company Phone', 
    render_kw={"class": "form-control col-sm-4"})
    
    dispatcher_name = StringField('Dispatcher\'s Name', 
    render_kw={"class": "form-control col-sm-4"})
    
    dispatcher_email = StringField('Dispatcher\'s Email',
    render_kw={"class": "form-control col-sm-4"})

    dispatcher_phone = StringField('Dispatcher\'s Phone', 
    render_kw={"class": "form-control col-sm-4"})
    
    carrier_company_name = StringField('Carrier', 
    render_kw={"class": "form-control col-sm-4"})
    
    equipment_details = StringField('Equipment Details', 
    render_kw={"class": "form-control col-sm-4"})

    bill_to = StringField('Bill To', 
    render_kw={"class": "form-control col-sm-4"})
    
    po_number = StringField('PO Number', 
    render_kw={"class": "form-control col-sm-4"})
    
    dock_number = StringField('Dock Number', 
    render_kw={"class": "form-control col-sm-4"})
    
    rate = StringField('Rate', 
    render_kw={"class": "form-control col-sm-4"})
    
    run_date = StringField('Job Date', 
    render_kw={"class": "form-control col-sm-4"})

    pickup_delivery_details = TextAreaField('Pickup and Delivery Details', 
    render_kw={"class": "form-control col-sm-4"})
    
    comments = TextAreaField('Comments', 
    render_kw={"class": "form-control col-sm-4"})
    
    created_at = StringField('Created on', 
    render_kw={"class": "form-control col-sm-4"})

    updated_at = StringField('Last Updated', 
    render_kw={"class": "form-control col-sm-4"})

    is_completed = SelectField('Is Completed', 
    choices=[('0', 'False'), ('1', 'True')])
    
    update = SubmitField('Update this Document', render_kw={"class":"btn sign-up"})

