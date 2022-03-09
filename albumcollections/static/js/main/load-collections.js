window.onload = function() {
    redirect_url = document.getElementById("redirect_url").getAttribute("data-redirect-url")
    window.location.replace(redirect_url)
}