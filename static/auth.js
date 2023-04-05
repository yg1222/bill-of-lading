

const emailValue = document.getElementById('email');
emailValue.addEventListener('input', function() {
  if (emailValue.validity.valid == false) {
    // console.log("Please enter a valid email address");
    // alert("Please enter a valid email address");

    emailValue.setCustomValidity('Please enter a valid email address');
  } else {
    emailValue.setCustomValidity('');
  }
});