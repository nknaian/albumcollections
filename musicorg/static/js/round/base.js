function fillRoundLinkTextbox(round_link) {
    var textbox = document.getElementById("roundLinkTextbox")
    textbox.value = round_link
}

function copyRoundLink() {
    /* Get the text field */
    var copyText = document.getElementById("roundLinkTextbox");

    /* Select the text field */
    copyText.select();
    copyText.setSelectionRange(0, 99999); /* For mobile devices */

    /* Copy the text inside the text field */
    document.execCommand("copy");
}

function confirmAndAdvance(confirm_msg) {
    /* Show a confirm message. If the user confirms, then show
    the loading screen and return true. If not, return false.
    */
    if (confirm(confirm_msg)) {
        $("#loading").show()
        $("#content").hide()
        return true
    }
    else {
        return false
    }
}