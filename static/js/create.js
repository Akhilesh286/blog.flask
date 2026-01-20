let isMax = false

document.getElementById("toggleTopbar").addEventListener('click',() => {
    if (isMax){
        document.getElementById("topbar-max").classList.add("topbar-hide")
        document.getElementById("topbar-mini").classList.remove("topbar-hide")
        isMax = false
    } else {
        document.getElementById("topbar-mini").classList.add("topbar-hide")
        document.getElementById("topbar-max").classList.remove("topbar-hide")
        isMax = true
    }
})