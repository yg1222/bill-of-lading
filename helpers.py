from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, request
from models.imports import Environment, io, pisa, send_file

print("Helpers imported")

def helpers_test():
    print("Helpers call test")

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
    files_list = os.listdir(UPLOAD_FOLDER)
    print("Emptying out the logos folder -> " + str(files_list))

    # loop through each file in the directory and delete it
    for file in files_list:
        file_path = os.path.join(UPLOAD_FOLDER, file)
        os.remove(file_path)


def render_sf_load_sheet(bol_html):
    bol_pdf = io.BytesIO()
    pisa.CreatePDF(bol_html, dest=bol_pdf)
    bol_pdf.seek(0)       

    return send_file(bol_pdf, as_attachment=False, download_name='bill_of_lading.pdf')
    #return bol_html