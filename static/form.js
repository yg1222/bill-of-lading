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
  var add_run_row = document.getElementById("add_run_row");
  var add_comments = document.getElementById("add_comments");

  // Initialize field counter to create unique names
  var pickFieldCounter = 0, delFieldCounter = 0;

  // Add rows for pickup and delivery details
  add_run_row.onclick = function (){   

    // Define run_row as a row the p/u and dlvry location and time
    additionalRunRow = document.createElement("tr");

    lblTimeDl = document.createElement("label"), lblTimePu = document.createElement("label");
    lblTimeDl.textContent = " Time: ";
    lblTimePu.textContent = " Time: ";

    puTD = document.createElement("td");
    puAddress= document.createElement("input");
    puTime= document.createElement("input");
    puAddress.setAttribute("type", "address");
    puAddress.setAttribute("name","pickup_location");
    puAddress.setAttribute("class","address");
    puTime.setAttribute("type","time");
    puTime.setAttribute("name","pickup_time");

    dlTD= document.createElement("td");
    dlAddress= document.createElement("input");
    dlTime= document.createElement("input");
    dlAddress.setAttribute("type", "address");
    dlAddress.setAttribute("name","delivery_location");
    dlAddress.setAttribute("class","address");
    dlTime.setAttribute("type","time");
    dlTime.setAttribute("name","delivery_time");

    // Insert the input element into the table data
    puTD.appendChild(puAddress);
    puTD.appendChild(lblTimePu);
    puTD.appendChild(puTime);

    dlTD.appendChild(dlAddress);
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
  

  add_comments.onclick = function(){
    commentLine = document.createElement("input");
    commentLine.setAttribute("type","text");
    commentLine.setAttribute("name","comments");

    // Get comment holder element
    commentHolder = document.getElementById("commentLineDiv");
    commentHolder.appendChild(commentLine);
  }

