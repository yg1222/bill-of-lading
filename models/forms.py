

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

