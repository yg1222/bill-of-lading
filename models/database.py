from models.imports import UserMixin, SQLAlchemy, datetime


# Initialize the SQLAlchemy object
db = SQLAlchemy()

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

# Companies table
class Companies(db.Model):
    id = db.Column(db.Integer,unique=True, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False, unique=True)    
    def __repr__(self):
        return '<Companies {}>'.format(self.company_name)

class PersonToCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    def __repr__(self):
        return '<PersonToCompany {}>'.format(self.id)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    company_name = db.Column(db.String(100))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    role = db.Column(db.String(150))
    feedback = db.Column(db.Text)
    rating = db.Column(db.String(50))
    suggestions = db.Column(db.Text)
    bug_reports = db.Column(db.Text)
    more_comments = db.Column(db.Text)
    def __repr__(self):
        return '<Feedback {}>'.format(self.id)

