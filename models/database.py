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
    stripe_customer_id = db.Column(db.String(100))  
    
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

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100))
    interval = db.Column(db.Interval)
    price = db.Column(db.Float)
    def __repr__(self):
        return '<Plan {}>'.format(self.id)


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    subscription_id = db.Column(db.String(100))
    def __repr__(self):
        return '<Feedback {}>'.format(self.id)


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


class BolDocuments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    guest_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    broker_company_name = db.Column(db.String(100))
    broker_company_address = db.Column(db.String(255))
    broker_company_phone = db.Column(db.String(50))
    dispatcher_name = db.Column(db.String(50))
    dispatcher_email = db.Column(db.String(100))
    dispatcher_phone = db.Column(db.String(50))
    carrier_company_name = db.Column(db.String(200))
    equipment_details = db.Column(db.String(200))
    bill_to = db.Column(db.String(200))
    po_number = db.Column(db.String(50))
    dock_number = db.Column(db.String(50))
    rate = db.Column(db.String(50))
    run_date = db.Column(db.String(50))
    pickup_delivery_details = db.Column(db.Text)
    comments = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return '<BolDocument {}>'.format(self.id)
