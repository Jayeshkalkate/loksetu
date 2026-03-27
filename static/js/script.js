document.addEventListener("DOMContentLoaded", function () {
    console.log("LokSetu Loaded 🚀");

    // Example: smooth scroll
    document.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
            console.log("Link clicked");
        });
    });
});