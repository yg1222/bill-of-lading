# Maybe a weather app that prints a joke on screen related to the weather

from flask import Flask, render_template, redirect, request, make_response
import pdfkit
pdfkit.configuration(wkhtmltopdf='usr/local/lib/python3.8/site-packages/wkhtmltopdf')

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/form", methods = ['GET', 'POST'])
def form():
    print("Console log test20")
    
    your_company_name = str(request.form.get("your_company_name"))
    logo_url = str(request.form.get("logo_url"))
    your_company_address = str(request.form.get("your_company_address"))
    your_company_phone = str(request.form.get("your_company_phone"))
    dispatcher_name = str(request.form.get("dispatcher_name"))
    dispatcher_email = str(request.form.get("dispatcher_email"))
    dispatcher_phone = str(request.form.get("dispatcher_phone"))
    run_date = str(request.form.get("run_date"))
    dock = str(request.form.get("dock"))
    to_company = str(request.form.get("to_company"))
    bill_to = str(request.form.get("bill_to"))
    quantity = str(request.form.get("quantity"))
    weight = str(request.form.get("weight"))
    rate = str(request.form.get("rate"))


    equipment_details = str(request.form.get("equipment_details"))
    pickup_location = str(request.form.get("pickup_location"))
    pickup_time = str(request.form.get("pickup_time"))
    delivery_location = str(request.form.get("delivery_location"))
    delivery_time = str(request.form.get("delivery_time"))
    comments = str(request.form.get("comments"))

    all_reminders = []
    all_reminders.append(str(request.form.get("reminder1")))
    all_reminders.append(str(request.form.get("reminder2")))
    all_reminders.append(str(request.form.get("reminder3")))
    all_reminders.append(str(request.form.get("reminder4")))
    
    print(all_reminders)

    reminders = []
    for rem in all_reminders:
        if rem != "":
            reminders.append(rem)
    
    print(reminders)


   

    bol_html =  render_template("bill_of_lading.html", your_company_name=your_company_name, logo_url=logo_url,your_company_phone=your_company_phone, your_company_address=your_company_address, 
                           dispatcher_name=dispatcher_name,dispatcher_email=dispatcher_email,dispatcher_phone=dispatcher_phone,
                           run_date=run_date,dock=dock,to_company=to_company,bill_to=bill_to,quantity=quantity,weight=weight,rate=rate,equipment_details=equipment_details,
                           pickup_location=pickup_location,pickup_time=pickup_time,delivery_location=delivery_location,delivery_time=delivery_time,comments=comments,
                           reminders=reminders)
    
    #pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

    bol_pdf = pdfkit.from_string(bol_html, False)
    pdf_response = make_response(bol_pdf)
    pdf_response.headers['Content-Type'] = 'application/pdf'
    pdf_response.headers['Content-Disposition'] = 'inline; filename=bill_of_lading.pdf'

    return pdf_response
    #return bol_html




if __name__ == '__main__':
    app.run(debug=True)