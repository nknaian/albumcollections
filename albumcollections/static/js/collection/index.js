/* Module Variables */

let playlist_id;

/* Sortable collection list */
// NOTE: I'm leaving this here just so I remember that I tested this out with a simple
// case. auto scroll is just really messed up. Especially with touch screen, but even destop
// doesn't work great. I don't know what to do. I think they just have bugs.
// Sortable.create(simpleList, {scrollSensitivity: 200, forceAutoscrollFallback: true});

// // Generate 100 items
// simpleList.innerHTML = Array.apply(null,  new Array(100)).map(function (v, i) {
//   return '<div class="list-group-item">item ' +
//     (i + 1) +
//     '</div>';
// }).join('');

var sortable_collection = new Sortable(collection_list, {
    disabled: true,
    scroll: true,
    forceAutoscrollFallback: true,
    scrollSensitivity: 30,
    scrollSpeed: 100,
    delay: 10,
    delayOnTouchOnly: true,
    forceFallback: true,  // This is necessary for mobile (although can't find any documentation saying so). Without this set, there's some other draggable animation that happens that interferes with sortablejs
    filter: '.incomplete_album',
    // handle: ".album-drag-handle",  // NOTE: This actually does work...maybe I'll want to use a design with this...
    onChoose: function (evt) {
        // Color the album card to indicate movement is active
        evt.item.querySelector(".album_card").classList.add('bg-primary')
        evt.item.querySelector(".album_card").classList.remove('bg-light')
    },
    onUnchoose: function (evt) {
        // Remove color from album card to indicate movement over
        evt.item.querySelector(".album_card").classList.add('bg-light')
        evt.item.querySelector(".album_card").classList.remove('bg-primary')       
    },
    onEnd: function (evt) {
        // Get the album ids of the albums needed to execute the reorder
        moved_album_id = evt.item.getAttribute('data-album_id')
        if (evt.item.nextElementSibling) {
            next_album_id = evt.item.nextElementSibling.getAttribute('data-album_id')
        }
        else {
            next_album_id = null
        }

        // Keep album card blue until movement completed (spotify api returns)
        evt.item.querySelector(".album_card").classList.add('bg-primary')
        evt.item.querySelector(".album_card").classList.remove('bg-light')

        $.post('/collection/reorder_collection', {
            data: JSON.stringify({
                playlist_id: playlist_id,
                moved_album_id: moved_album_id,
                next_album_id: next_album_id
            }),
            contentType: 'application/json'
        }).done(function (response) {
            if (response["success"]) {
                // Remove color from album card to indicate movement locked in (spotify api returned)
                evt.item.querySelector(".album_card").classList.add('bg-light')
                evt.item.querySelector(".album_card").classList.remove('bg-primary')        
            }
            else {
                // Color the album card red to indicate a failure with spoitify api
                evt.item.querySelector(".album_card").classList.add('bg-danger')
                evt.item.querySelector(".album_card").classList.remove('bg-primary')     

                alert(`Sorry, failed to reorder collection.\n\n${response["exception"]}`)   
            }
        }).fail(function() {
            alert("Sorry, a server failure occured.")
        });
    }
});


/* Functions */

function init(play_id, play_owner_id, user_id) {
    playlist_id = play_id

    /* Hide buttons that are only usable if user is logged in */
    console.log(user_id)
    if (user_id === "None") {
        $('#add_album').hide()
    } else {
        $('#add_album').show()
    }

    /* Hide buttons that are only usable if the user owns the collection */
    if (play_owner_id === user_id) {
        $('#shuffle_collection').show()
        $('#reorder_collection').show()
        $('#album_control_modal_remove').show()
    } else {
        $('#shuffle_collection').hide()
        $('#reorder_collection').hide()
        $('#album_control_modal_remove').hide()
    }
}

/* Event Listeners */

document.querySelectorAll('.album_card').forEach(item => {
    item.addEventListener("click", function() {
        // Only open the modal of reording is not active
        if (!document.getElementById('reorder-active').checked) {
            // Get the album item that was clicked
            album_item = this.closest('.album_item')

            // Set the album contorl modal's target album item id
            document.getElementById("album_control_modal").setAttribute("data-target_album_item_id", album_item.id)

            // Set album image properties in modal
            album_control_modal_img = document.getElementById("album_control_modal_img")

            img_url = album_item.getAttribute("data-album_img_url")
            if (img_url) {
                album_control_modal_img.src = img_url
            }
            else {
                album_control_modal_img.src
            }

            album_control_modal_img.alt = album_item.getAttribute("data-album_name")

            // Set spotify link properties in modal
            album_control_modal_sp_link = document.getElementById("album_control_modal_spotify_link")
            album_control_modal_sp_link.href = album_item.getAttribute("data-album_link")

            // Set the album title in album control modal and album move modal
            album_control_modal_title = document.getElementById("album_control_modal_title")
            album_control_modal_title.innerHTML = `<b>${album_item.getAttribute("data-album_name")}</b> by ${album_item.getAttribute("data-album_artists")}`
            album_move_modal_title = document.getElementById("album_move_modal_title")
            album_move_modal_title.innerHTML = `<b>${album_item.getAttribute("data-album_name")}</b> by ${album_item.getAttribute("data-album_artists")}`

            // Open the modal
            $('#album_control_modal').modal('show')
        }
    });
})

document.getElementById("add_album").addEventListener("click", function() {
    // Hide the album control modal so that the move album modal shows
    $('#album_control_modal').modal('hide')
})

document.getElementById("add_album_modal_close_btn").addEventListener("click", function() {
    // Bring back the album control modal
    $('#album_control_modal').modal('show')
})

document.getElementById("add_album_submit").addEventListener("click", function() {
    // Get selected destination collection
    dest_collection_id = $("#collectionMoveSelect option:selected").val()

    // Get album item
    album_item = document.getElementById(
        document.getElementById("album_control_modal").getAttribute("data-target_album_item_id")
    )

    // Get album id
    album_id = album_item.getAttribute("data-album_id")

    // Bring back album control modal into focus
    $('#add_album_modal').modal('hide')
    $('#album_control_modal').modal('show')

    // Make server post to do the add
    $.post('/collection/add_album', {
        dest_collection_id: dest_collection_id,
        album_id: album_id
    }).done(function (response) {
        if (response["success"]) {
            // If the album was added to this collection and album was incomplete, remove the "incomplete_album" class
            console.log("removing incomplete_album tag")
            if (dest_collection_id === playlist_id) {
                album_item.classList.remove("incomplete_album")
            }
        } else {
            alert(`Sorry, failed to add album.\n\n${response["exception"]}`)
        }
    }).fail(function() {
        alert("Sorry, a server failure occured.")
    });
})

document.getElementById("album_control_modal_remove").addEventListener("click", function() {
    album_item = document.getElementById(
        document.getElementById("album_control_modal").getAttribute("data-target_album_item_id")
    )
    album_id = album_item.getAttribute("data-album_id")
    album_name = album_item.getAttribute("data-album_name")

    if (confirm(`Are you sure you want to remove ${album_name} from the collection?`)) {
        $('.remove_album_load_item').show()
        $('.album_control_bar').hide()
        $.post('/collection/remove_album', {
            playlist_id: playlist_id,
            album_id: album_id
        }).done(function (response) {
            if (response["success"]) {
                $('.remove_album_load_item').hide()
                $('.album_control_bar').show()
                $(album_item).hide()
                $('#album_control_modal').modal('hide')
            }
            else {
                $('.remove_album_load_item').hide()
                $('.album_control_bar').show()
                alert(`Sorry, failed to remove album.\n\n${response["exception"]}`)
            }
        }).fail(function() {
            $('.remove_album_load_item').hide()
            $('.album_control_bar').show()
            alert("Sorry, a server failure occured.")
        });
    }
});

document.getElementById('reorder-active').addEventListener("change", function() {
    // Enable sorting of the list of albums based on the 'reorder-active' checkbox
    // Apply styling dependent on whether reordering is active
    if (this.checked) {
        sortable_collection.option("disabled", false)

        var elements = document.getElementsByClassName('album_item')
        for(var i = 0; i < elements.length; i++) {
            elements[i].style.cursor = "grab";
        }
        var elements = document.getElementsByClassName('incomplete_album')
        for(var i = 0; i < elements.length; i++) {
            elements[i].style.cursor = "default"
        }

        var elements = document.getElementsByClassName('album_img')
        for(var i = 0; i < elements.length; i++) {
            elements[i].style.opacity = 0.5
        }

        var elements = document.getElementsByClassName('album-item-move-container')
        for(var i = 0; i < elements.length; i++) {
            elements[i].classList.add('card-img-overlay')
        }

        var elements = document.getElementsByClassName('album-item-move')
        for(var i = 0; i < elements.length; i++) {
            element = elements[i]
            if (!element.closest('.album_item').classList.contains('incomplete_album')) {
                $(element).show()
            }
        }

        var elements = document.getElementsByClassName('album_card')
        for(var i = 0; i < elements.length; i++) {
            element = elements[i]
            if (element.closest('.album_item').classList.contains('incomplete_album')) {
                element.classList.remove('bg-light')
                element.classList.add('bg-danger')
            }
        }
    }
    else {
        sortable_collection.option("disabled", true)

        var elements = document.getElementsByClassName('album_item')
        for(var i = 0; i < elements.length; i++) {
            elements[i].style.cursor = "default";
        }

        var elements = document.getElementsByClassName('album_img')
        for(var i = 0; i < elements.length; i++) {
            elements[i].style.opacity = 1;
        }

        var elements = document.getElementsByClassName('album-item-move-container')
        for(var i = 0; i < elements.length; i++) {
            elements[i].classList.remove('card-img-overlay')
        }

        var elements = document.getElementsByClassName('album-item-move')
        for(var i = 0; i < elements.length; i++) {
            $(elements[i]).hide()
        }

        var elements = document.getElementsByClassName('album_card')
        for(var i = 0; i < elements.length; i++) {
            element = elements[i]
            if (element.closest('.album_item').classList.contains('incomplete_album')) {
                element.classList.add('bg-light')
                element.classList.remove('bg-danger')
            }
        }
    }
})