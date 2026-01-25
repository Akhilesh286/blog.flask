let isComment = false

document.getElementById("toggle-comment").addEventListener("click", () => {
    console.log("hellow");
    
    if (isComment){
        document.getElementById("comment-box").classList.add("hide-comment")
        isComment = false
    }else {
        document.getElementById("comment-box").classList.remove("hide-comment")
        isComment = true
    }
})


const box = document.querySelector(".comment-box");
const handle = document.querySelector(".resize-handle");

handle.addEventListener("mousedown", startDrag);

function startDrag(e) {
    document.addEventListener("mousemove", resize);
    document.addEventListener("mouseup", stopDrag);
}

function resize(e) {
    const newWidth = window.innerWidth - e.clientX;
    box.style.width = newWidth + "px";
}

function stopDrag() {
    document.removeEventListener("mousemove", resize);
    document.removeEventListener("mouseup", stopDrag);
}


// Comment Input
const input = document.getElementById("chatInput");

input.addEventListener("input", () => {
    input.style.height = "auto"; // reset height
    input.style.height = Math.min(input.scrollHeight, 150) + "px"; // max auto-expand height
});


// Toogle comment replies 
