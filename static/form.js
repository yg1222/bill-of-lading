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
  