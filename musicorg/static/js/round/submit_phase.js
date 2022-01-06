/* Module Variables */

let spotify_search_bar = document.getElementById('spotify_search_bar');
let spotify_search_timeout = null;
let spotify_search_results = []


/* Functions */

function get_spotify_album_search_results() {
    /* Wrapper to call get_spotify_search_results with
     * 'album' as the music type
     * 
     * NOTE: I haven't figured out how to pass in a 
     * jinja2 variable to get_spotify_search_results
     * from within a wtf form field...so this is a workaround.
     */
    get_spotify_search_results("album")
}

function get_spotify_track_search_results() {
    /* Wrapper to call get_spotify_search_results with
     * 'track' as the music type
     * 
     * NOTE: I haven't figured out how to pass in a 
     * jinja2 variable to get_spotify_search_results
     * from within a wtf form field...so this is a workaround.
     */
    get_spotify_search_results("track")
}

function get_spotify_search_results(music_type) {
    /* Use the /round/spotify_search route to display music results
     * based on the user's entered text from the backend.
     * The search will only be executed after 1000ms has elapsed
     * since the previous time this function was called.
     */

    // Clear the timeout if it has already been set.
    // This will prevent the previous task from executing
    // if it has been less than <MILLISECONDS>
    clearTimeout(spotify_search_timeout);

    // Make a new timeout set to go off in 1000ms (1 second)
    spotify_search_timeout = setTimeout(function () {
        fetch('/round/spotify_search', {

            // Declare what type of data we're sending
            headers: {
              'Content-Type': 'application/json'
            },
        
            // Specify the method
            method: 'POST',
        
            // A JSON payload
            body: JSON.stringify({
                "search_text": spotify_search_bar.value,
                "music_type": music_type
            })
        }).then(function (response) {
            return response.json();
        }).then(function (response_json) {
            // Clear current search results
            for(var i = 0, size = 20; i < size ; i++) { 
                $(`#music_result_${i}`).hide()
            }
            spotify_search_results = []

            // Hide the form submission errors
            $("#spotify_link_form_errors").hide()

            // If the link was invalid, show a corresponding error message
            if (response_json["invalid_link"]) {
                $("#music_search_invalid_link").show()
                $("#music_search_no_results_found").hide()
            }
            // If the music results are empty, show a corresponding error message
            else if (!Object.keys(response_json["music_results"]).length) {
                $("#music_search_no_results_found").show()
                $("#music_search_invalid_link").hide()
            }
            // Otherwise, save and show the obtained music results
            else {
                for(var i = 0, size = response_json["music_results"].length; i < size ; i++) {
                    music_result = response_json["music_results"][i]
                    spotify_search_results.push(music_result)
                    populate_music_result(music_result, i)
                }
    
                $("#music_search_no_results_found").hide()
                $("#music_search_invalid_link").hide()
            }
        });
    }, 1000);
}

function choose_music(result_index) {
    /* Remove all other music results besides the one
     * at the give index, and put the link of the chosen
     * music into the search bar.
     */
    spotify_search_bar.value = spotify_search_results[result_index]["music_link"]

    for(var i = 0, size = 20; i < size ; i++) { 
        if (result_index != i) {
            $(`#music_result_${i}`).hide()
        }
    }
    $("#music_search_no_results_found").hide()
    $("#music_search_invalid_link").hide()
}

function populate_music_result(music_result, result_index) {
    /* Helper function to put music information in a music result
     * HTML element and show it.
     */

    let music_result_img = document.getElementById(`music_result_img_${result_index}`);
    let music_result_name = document.getElementById(`music_result_name_${result_index}`)

    music_result_img.src = music_result["music_img_url"]
    music_result_img.alt = music_result["music_name"]
    music_result_name.innerHTML = music_result["music_name"]

    $(`#music_result_${result_index}`).show()
}
