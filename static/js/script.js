$(document).ready(function() {
    // When the button with id "toggleButton" is clicked
    $('#toggleButton').click(function() {
        // Toggle the visibility of the paragraph with id "myParagraph"
        $('#myParagraph').toggle();
    });
});


// back button 
document.getElementById("backBtn").addEventListener("click", () => {
    window.history.back();
});