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