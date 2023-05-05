function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
  
    // Hide all tab content elements
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
  
    // Remove the "active" class from all tab links
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
  
    // Show the selected tab content and set the clicked tab link to active
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
  }

  // Getting buttons
  var addRunRow = document.getElementById("add_run_row");
  var addComments = document.getElementById("add_comments");

  // Initialize field counter to create unique names
  var pickFieldCounter = 0, delFieldCounter = 0;

  // Add rows for pickup and delivery details
  addRunRow.onclick = function (){   

    // Define run_row as a row the p/u and dlvry location and time
    additionalRunRow = document.createElement("tr");

    lblTimeDl = document.createElement("label"), lblTimePu = document.createElement("label");
    lblTimeDl.textContent = " Time: ";
    lblTimePu.textContent = " Time: ";

    // Creating pickup elements
    puTD = document.createElement("td");
    puCompany = document.createElement("input");
    puContacts = document.createElement("input");
    puAddress= document.createElement("input");
    puTime= document.createElement("input");
    puCompany.setAttribute("type", "text");
    puCompany.setAttribute("name","pickup_company");
    puCompany.setAttribute("class","companies");
    puCompany.setAttribute("placeholder","Sending Company");
    puContacts.setAttribute("type", "text");
    puContacts.setAttribute("name","pickup_contact");
    puContacts.setAttribute("class","contacts");
    puContacts.setAttribute("placeholder","Contact info");
    puAddress.setAttribute("type", "address");
    puAddress.setAttribute("name","pickup_location");
    puAddress.setAttribute("class","address");
    puAddress.setAttribute("placeholder","Address");
    puTime.setAttribute("type","time");
    puTime.setAttribute("name","pickup_time");
    puTime.setAttribute("class","time");

    // Creating delivery elements 
    dlTD= document.createElement("td");
    dlCompany = document.createElement("input");
    dlContacts = document.createElement("input");
    dlAddress= document.createElement("input");
    dlTime= document.createElement("input");
    dlCompany.setAttribute("type", "text");
    dlCompany.setAttribute("name","delivery_company");
    dlCompany.setAttribute("class","companies");
    dlCompany.setAttribute("placeholder","Receiving Company");
    dlContacts.setAttribute("type", "text");
    dlContacts.setAttribute("name","delivery_contact");
    dlContacts.setAttribute("class","contacts");
    dlContacts.setAttribute("placeholder","Contact info");
    dlAddress.setAttribute("type", "address");
    dlAddress.setAttribute("name","delivery_location");
    dlAddress.setAttribute("class","address");
    dlAddress.setAttribute("placeholder","Address");
    dlTime.setAttribute("type","time");
    dlTime.setAttribute("name","delivery_time");
    dlTime.setAttribute("class","time");

    // Insert/Display the input element to the table data
    puTD.appendChild(document.createElement("hr"));
    puTD.appendChild(puCompany);
    puTD.appendChild(document.createElement("br"));
    puTD.appendChild(puContacts);
    puTD.appendChild(document.createElement("br"));
    puTD.appendChild(puAddress);
    puTD.appendChild(document.createElement("br"));
    puTD.appendChild(lblTimePu);
    puTD.appendChild(puTime);

    dlTD.appendChild(document.createElement("hr"));
    dlTD.appendChild(dlCompany);
    dlTD.appendChild(document.createElement("br"));
    dlTD.appendChild(dlContacts);
    dlTD.appendChild(document.createElement("br"));
    dlTD.appendChild(dlAddress);
    dlTD.appendChild(document.createElement("br"));
    dlTD.appendChild(lblTimeDl);
    dlTD.appendChild(dlTime);

    // Insert the table data into the row
    additionalRunRow.appendChild(puTD);
    additionalRunRow.appendChild(dlTD);    
    
    console.log(additionalRunRow);
    // Append th additionalRow to the run_table
    run_table = document.getElementById("run_table");
    run_table.appendChild(additionalRunRow);    
  }
  

  addComments.onclick = function(){
    commentLine = document.createElement("input");
    commentLine.setAttribute("type","text");
    commentLine.setAttribute("name","comments");

    // Get comment holder element
    commentHolder = document.getElementById("commentLineDiv");
    commentHolder.appendChild(commentLine);
  }

