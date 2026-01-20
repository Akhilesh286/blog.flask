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


// CodeMirror
const cm = CodeMirror.fromTextArea(document.getElementById("editor"), {
  mode: "markdown",
  lineNumbers: true,
  lineWrapping: true,
  theme: "dracula"
});

const preview = document.getElementById("preview");

// Markdown preview update
cm.on("change", () => {
    preview.innerHTML = marked.parse(cm.getValue());
});

// GRID SPLITTER
const wrapper = document.getElementById("wrapper");
const splitter = document.getElementById("splitter");

let dragging = false;

splitter.addEventListener("mousedown", () => {
    dragging = true;
    document.body.style.cursor = "col-resize";
});

document.addEventListener("mousemove", (e) => {
    if (!dragging) return;

    const totalWidth = wrapper.offsetWidth;

    let leftWidth = e.clientX;

    // Boundaries
    if (leftWidth < 200) leftWidth = 200;
    if (leftWidth > totalWidth - 200) leftWidth = totalWidth - 200;

    // Set grid columns directly
    wrapper.style.gridTemplateColumns = `${leftWidth}px 6px 1fr`;
});

document.addEventListener("mouseup", () => {
    dragging = false;
    document.body.style.cursor = "default";
});


// action buttons
document.getElementById("h1").addEventListener("click", () => {
    cm.replaceSelection("# ");
    cm.focus();
});
document.getElementById("h2").addEventListener("click", () => {
    cm.replaceSelection("## ");
    cm.focus();
});
document.getElementById("h3").addEventListener("click", () => {
    cm.replaceSelection("### ");
    cm.focus();
});
document.getElementById("h4").addEventListener("click", () => {
    cm.replaceSelection("#### ");
    cm.focus();
});
document.getElementById("h5").addEventListener("click", () => {
    cm.replaceSelection("##### ");
    cm.focus();
});
document.getElementById("h6").addEventListener("click", () => {
    cm.replaceSelection("###### ");
    cm.focus();
});
