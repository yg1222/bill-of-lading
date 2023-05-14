import importlib
from helpers import login_required
from models.imports import Blueprint, render_template, request, current_app, \
    current_user
from models.database import db, Companies, Feedback, BolDocuments


bp = Blueprint("routes_r", __name__)


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
        # Create a list of host records
        host_records = BolDocuments.query.filter_by(host_id=current_user.id).all()
        print(host_records)
        
        # Creates a list of forms with the data from each from the host_records list
        host_forms = [RecordForm(obj=host_record) for host_record in host_records]

        # Create a list of guest records

        return render_template("portal.html", form=record_form, host_forms=host_forms)
