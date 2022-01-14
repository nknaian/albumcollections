/* Module Variables */

let num_albums = 0;
let show_album = [];
let playlist_id;

function init(n_albums, play_id) {
    console.log(`inited ${play_id}`)

    num_albums = n_albums

    for(var i = 0, size = num_albums; i < size ; i++) { 
        show_album.push(true)
    }

    playlist_id = play_id
}

/* Functions */

function remove_album(album_index) {

    console.log(`album_index = ${album_index}`)

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
            $(`#album_remove_${album_index}`).hide()
            show_album[i] = false
        }
    });
}

function enable_remove_albums() {
    console.log("Enable remove albums")
    
    $("#enable_remove_albums_btn").hide()
    $("#disable_remove_albums_btn").show()

    console.log(`num albums = ${num_albums}`)

    for(var i = 0, size = num_albums; i < size ; i++) { 
        $(`#album_link_${i}`).hide()

        if (show_album[i]) {
            $(`#album_remove_${i}`).show()
        }
    }

    console.log("all done enabling")
}

function disable_remove_albums() {
    console.log("Disable remove albums")

    $("#enable_remove_albums_btn").show()
    $("#disable_remove_albums_btn").hide()

    for(var i = 0, size = num_albums; i < size ; i++) { 
        $(`#album_remove_${i}`).hide()

        if (show_album[i]) {
            $(`#album_link_${i}`).show()
        }
    }
}