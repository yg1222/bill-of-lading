from models.imports import UserMixin, SQLAlchemy, datetime, JSON, ARRAY,\
Integer


# Initialize the SQLAlchemy object
db = SQLAlchemy()

# Organizations
class Organizations(db.Model):
    __tablename__ = "organizations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(JSON)
    owner = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_org_owner'))
    settings = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    def __repr__(self):
        return f'<Organization: (id={self.id}, name={self.name})>'
    
# Person Table
class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)    
    username = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True)
    address = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    password_hash = db.Column(db.String(1000))
    is_verified = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(100))    
    user_settings = db.Column(JSON)
    orginization = db.Column(db.Integer, db.ForeignKey('organizations.id', name='fk_user_org'))
    def __repr__(self):
        return f'<User {self.username}>'


class Plans(db.Model):
    __tablename__ = "plans"
    id = db.Column(db.Integer, primary_key=True)
    stripe_plan_id = db.Column(db.String(100), unique=True)
    plan_name = db.Column(db.String(100))
    interval = db.Column(db.String)
    price = db.Column(db.Integer)
    def __repr__(self):
        return f'<Plan {self.stripe_plan_id}>'


class Subscriptions(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    stripe_customer_id = db.Column(db.String(100))
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id', name='fk_subscription_plan'))
    start_date = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    subscription_id = db.Column(db.String(100), unique=True, nullable=False)
    def __repr__(self):
        return f'<Subscription {self.id}>'


class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_feedback_user'), nullable=False)
    company_name = db.Column(db.String(100))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    role = db.Column(db.String(150))
    feedback = db.Column(db.Text)
    rating = db.Column(db.String(50))
    suggestions = db.Column(db.Text)
    bug_reports = db.Column(db.Text)
    more_comments = db.Column(db.Text)
    def __repr__(self):
        return f'<Feedback {self.id}>'


class LoadSheets(db.Model):
    __tablename__ = "load_sheets"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_load_sheet_owner'))
    load_sheet = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    def __repr__(self):
        return f'<LoadSheet {self.id}>'
    

class BolDocuments(db.Model):
    __tablename__ = "bol_documents"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_bol_owner'))
    involved_users = db.Column(ARRAY(db.Integer))
    bol_document = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    def __repr__(self):
        return f'<BolDocument {self.id}>'
    

class Companies(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_company_owner'))
    user_link = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_company_user_link'))
    company = db.Column(JSON)
    type = db.Column(db.String(40))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    def __repr__(self):
        return f'<Company {self.id}>'
    
class AutoSuggestions(db.Model):
    __tablename__ = "auto_suggestions"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_auto_suggest_user'))
    type = db.Column(db.String(50))
    text = db.Column(db.Text)
    def __repr__(self):
        return f'<AutoSuggestion {self.id}>'


# Payment Handling
# Idempotency Table
class IdempotentRequests(db.Model):
    __tablename__ = "idempotent_requests"    
    id = db.Column(db.Integer, primary_key=True)
    idempotency_key = db.Column(db.String(255))
    sf_user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_idr_user'))    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    generated_in = db.Column(db.String(100))
    generated_by = db.Column(db.String(100))
    def __repr__(self):
        return f'<IdempotentRequest {self.idempotency_key}>'


# Webhook Table
class WebhookResponses(db.Model):
    __tablename__ = "webhook_responses"
    id = db.Column(db.Integer, primary_key=True)
    idempotency_key_id = db.Column(db.Integer, db.ForeignKey('idempotent_requests.id', name='fk_webhook_idem_id'))
    evt_type = db.Column(db.String(100))
    evt_id = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<WebhookResponse {self.evt_id}>'


# BOL Numbers
class BolNumbers(db.Model):
    __tablename__ = 'bol_numbers'
    id = db.Column(db.Integer, primary_key=True)
    bol_number = db.Column(db.String(100))
    owner = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_bol_number_owner'))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<BolNumber {self.id}-{self.bol_number}>'
    
# Audit Trail
class AuditTrail(db.Model):
    __tablename__ = "audit_trail"
    id = db.Column(db.Integer, primary_key=True)
    bol_document_id = db.Column(db.Integer, db.ForeignKey('bol_documents.id', name='fk_audit_bol'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_audit_user'))
    action = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<AuditTrail {self.id}-{self.action}>'

