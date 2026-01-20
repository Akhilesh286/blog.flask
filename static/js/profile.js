let isEdit = true
document.querySelector('#edit').addEventListener('click', () => {
    console.log('called');
    if (isEdit){
        document.querySelector('#submit').style.display = 'block'
        document.querySelector('#pic').style.display = 'block'  
        document.querySelectorAll('.lock').forEach(input => {
            input.disabled = false;
        });
        isEdit = false
    } else {
        document.querySelector('#submit').style.display = 'none'
        document.querySelector('#pic').style.display = 'none'  
        document.querySelectorAll('.lock').forEach(input => {
            input.disabled = true;
            input.value = ''
        });
        isEdit = true
    }

})
document.getElementById("pic").addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (!file) return;

    const img = document.getElementById("profilePreview");
    img.src = URL.createObjectURL(file);
});