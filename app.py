# Bill of Lading Generator
# Author: YGJ

from flask import Flask, render_template, redirect, request, make_response, send_file
from xhtml2pdf import pisa
import io
import os
from itertools import zip_longest


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/form", methods = ['GET', 'POST'])
def form():
    print("Request triggered")
    
    if request.method == "POST":           
        
        # Getting values from the form
        your_company_name = str(request.form.get("your_company_name"))    
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
        
        # Lists
        pickup_locations = request.form.getlist("pickup_location")
        pickup_times = request.form.getlist("pickup_time")
        delivery_locations = request.form.getlist("delivery_location")
        delivery_times = request.form.getlist("delivery_time")
        comments = request.form.getlist("comments")
        
        # Files
        # TODO: check for existense
        try:
            logo = request.files["logo"]
            logo_path = os.path.join(app.instance_path, logo.filename)
            print(logo_path)
            logo.save(logo_path)
            print(logo_path)    
        except FileNotFoundError:
            print("Error getting logo")
        
        
        # Logging lists
        print(pickup_locations)
        print(pickup_times)
        print(delivery_locations)
        print(delivery_times)
        print(comments)
        
        comments_formatted =  [x for x in comments if x != '']
        print(comments_formatted)
        

        # Create a new list of dictionaries {"Address":value, "Time":value} for pickup locations
        
        
        pickup_tuples = list(zip_longest(pickup_locations, pickup_times, fillvalue="None"))
        delivery_tuples =list(zip_longest(delivery_locations, delivery_times, fillvalue="None"))
        #[
            # ('123 queensway', '15:14'),
            # ('123 queensway', '16:14'),
            # ('123 queensway', '16:14')
        # ]
        
        # Create a list of dictionaries with pu_address and pu_time
        pickup_details =[]
        for t in pickup_tuples:
            temp_dict = {"pu_address":t[0],"pu_time":t[1]}
            pickup_details.append(temp_dict)    
        print ("pickup_details ↓")       
        print(pickup_details)
        
        # Create a new list of dictionaries {"Address":value, "Time":value} foe delivery locations
        delivery_details = []
        for t in delivery_tuples:
            temp_dict = {"del_address":t[0],"del_time":t[1]}
            delivery_details.append(temp_dict)                
        print ("delivery_details ↓")    
        print(delivery_details)
        
        # TODO: Clean up details in such a way that if that the pickup maps to the delivery and handle blank addresses
        # Use itertoolz 
        pickup_delivery_details_zipped = zip_longest(pickup_details, delivery_details, fillvalue="None")
        pickup_delivery_details = list(pickup_delivery_details_zipped)    
        print("pickup_delivery_details ↓")
        print(pickup_delivery_details)
        
        # Format of pickeup_delivered_details ↓
        # [
        #     (  
        #         {'pu_address': '123 queensway', 'pu_time': '15: 17'},
        #         {'del_address': '456 kinsway', 'del_time': '15: 17'}    
        #     ), 
        #     (
        #         {'pu_address': '321 queensway', 'pu_time': '16: 18'},
        #         {'del_address': '5656  kinsway', 'del_time': '15: 18'}
        #     ), 
        #     (
        #         {'pu_address': '777 queensway', 'pu_time': '18: 18'},
        #         {'del_address': '987 kinsway', 'del_time': '19: 24'}
        #     )
        # ]
        

        bol_html =  render_template("bill_of_lading.html", your_company_name=your_company_name,logo_path=logo_path,your_company_phone=your_company_phone, your_company_address=your_company_address, 
                            dispatcher_name=dispatcher_name,dispatcher_email=dispatcher_email,dispatcher_phone=dispatcher_phone,
                            run_date=run_date,dock=dock,to_company=to_company,bill_to=bill_to,quantity=quantity,weight=weight,rate=rate,equipment_details=equipment_details,
                            pickup_delivery_details=pickup_delivery_details,comments=comments_formatted,
                            )
        
        #pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

        bol_pdf = io.BytesIO()
        pisa.CreatePDF(bol_html, dest=bol_pdf)
        bol_pdf.seek(0)
        # pdf_response.headers['Content-Type'] = 'application/pdf'
        # pdf_response.headers['Content-Disposition'] = 'inline; filename=bill_of_lading.pdf'

        return send_file(bol_pdf, as_attachment=False, download_name='bill_of_lading.pdf')
        #return pdf_response
        #return bol_html


        # Emptying out the logos directory
       
        # List of files in directory
        files_in_logos = os.listdir(logos_path)

        # loop through each file in the directory and delete it
        for file in files_in_logos:
            file_path = os.path.join(logos_path, file)
            os.remove(file_path)


if __name__ == '__main__':
    app.run(debug=True)