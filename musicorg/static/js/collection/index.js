/* Module Variables */

let num_albums = 0;
let playlist_id;

function init(n_albums, play_id) {
    num_albums = n_albums

    playlist_id = play_id
}

/* Functions */

function remove_album(album_index, album_name) {
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
                "album_index": album_index
            })
        }).then(function (response) {
            return response.json();
        }).then(function (response_json) {
            if (response_json["success"]) {
                $(`#album_${album_index}`).hide()
            }
        });
    }
}
