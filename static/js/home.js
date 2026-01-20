
let page = 2;
let loading = false;

window.addEventListener("scroll", async () => {
    console.log("working");
    if (loading) return;

    const nearBottom =
        window.innerHeight + window.scrollY >= document.body.offsetHeight - 200;

    if (!nearBottom) return;

    loading = true;
    document.getElementById("loader").style.display = "block";

    const res = await fetch(`/posts/load?page=${page}`);
    const html = await res.text();

    if (html.trim() === "") {
        window.removeEventListener("scroll", this);
        return;
    }

    document.getElementById("post-container")
        .insertAdjacentHTML("beforeend", html);

    page++;
    loading = false;
    document.getElementById("loader").style.display = "none";
});
