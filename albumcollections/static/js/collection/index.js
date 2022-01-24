/* Module Variables */

let playlist_id;

/* Functions */

function init(play_id) {
    playlist_id = play_id
}

function remove_album(album_name, album_id) {
    if (confirm(`Are you sure you want to remove ${album_name} from the collection?`)) {
        fetch(`/collection/remove_album`, {

            // Declare what type of data we're sending
            headers: {
                'Content-Type': 'application/json'
            },

            // Specify the method
            method: 'POST',

            // A JSON payload
            body: JSON.stringify({
                "playlist_id": playlist_id,
                "album_id": album_id
            })
        }).then(function (response) {
            return response.json();
        }).then(function (response_json) {
            if (response_json["success"]) {
                $(`#${album_id}`).hide()
            }
            else {
                alert(`Sorry, failed to remove album.\n\n${response_json["exception"]}`)
            }
        });
    }
}
