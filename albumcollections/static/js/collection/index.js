/* Module Variables */

let playlist_id;
let device_select = document.getElementById("device_select")
let devices = {};
let start_album_id = null
let shuffle_albums = false
let user_logged_in = false

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

function init(play_id, logged_in) {
    playlist_id = play_id
    user_logged_in = logged_in

    /* Hide buttons that are only usable if logged in */
    if (!logged_in) {
        $('#play_collection').hide()
        $('#shuffle_play_collection').hide()
        $('#reorder_collection').hide()
        $('#album_control_modal_remove').hide()
    }
}

function device_play_select() {
    /* Get spotify devices that can be played from, then
    close the control window and open the device select
    window.

    If there's no avaiable devices then raise an alert.
    */
   // Hide the loading screen upon opening up the device play modal
   $(".device_play_load_item").hide()

    $.post('/collection/get_devices', {
        data: JSON.stringify({}),
        contentType: 'application/json'
    }).done(function (response) {
        if (response["exception"]) {
            alert(`Sorry, failed to play collection.\n\n${response["exception"]}`)
        }
        else if (response["devices"]) {
            // Clear device select options
            device_select.options.length = 0

            // Update devices from server
            devices = response["devices"]

            // Update device select options from server
            for(var device in devices) {
                device_select.options[device_select.options.length] = new Option(device)
            }

            if (device_select.options.length) {
                // Show the device select modal
                $('#select_device_modal').modal('show')

                // Hide the album control modal
                $('#album_control_modal').modal('hide')
            }
            else {
                // Alert that no devices are avaiable
                alert('No devices available to play from. Please open spotify on a device and try again.')
            }
        }
    }).fail(function() {
        alert("Sorry, a server failure occured.")
    });
}

function play_collection(device_id) {
    /* Play the collection using start album
    from the given device
    */
   // Show the loading screen, as play request is about to start
    $(".device_play_load_item").show()

    // Make the request to play the collection
    $.post('/collection/play_collection', {
        data: JSON.stringify({
            playlist_id: playlist_id,
            device_id: device_id,
            start_album_id: start_album_id,
            shuffle_albums: shuffle_albums 
        }),
        contentType: 'application/json'
    }).done(function (response) {
        // Hide the loading screen, as we're now done making the play request
        $('.device_play_load_item').hide()

        // Alert w/ error
        if (response["exception"]) {
            alert(`Sorry, failed to play collection.\n\n${response["exception"]}`)
        }
    }).fail(function() {
        // Hide the loading screen, as we're now done making the play request
        $('.device_play_load_item').hide()

        // Alert that server failure occurred (this shouldn't happen!)
        alert("Sorry, a server failure occured.")
    });
}

/* Event Listeners */

document.querySelectorAll('.album_card').forEach(item => {
    item.addEventListener("click", function() {
        // Only open the modal of reording is not active
        if (!document.getElementById('reorder-active').checked) {
            // Get the album item that was clicked
            album_item = this.closest('.album_item')

            // Show or hide the play button in the album modal. Only show if the user
            // is logged in and also the album is complete (album object contains tracks)
            if (user_logged_in && album_item.classList.contains("complete_album")) {
                $('#play_collection_from_album').show()
            } else {
                $('#play_collection_from_album').hide()
            }

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

            // Set the album title in modal
            album_control_modal_title = document.getElementById("album_control_modal_title")
            album_control_modal_title.innerHTML = `<b>${album_item.getAttribute("data-album_name")}</b> by ${album_item.getAttribute("data-album_artists")}`

            // Open the modal
            $('#album_control_modal').modal('show')
        }
    });
})

document.getElementById("play_collection").addEventListener("click", function() {
    start_album_id = null
    shuffle_albums = false
    device_play_select()
});

document.getElementById("shuffle_play_collection").addEventListener("click", function() {
    start_album_id = null
    shuffle_albums = true
    device_play_select()
});

document.getElementById("play_collection_from_album").addEventListener("click", function() {
    album_item = document.getElementById(
        document.getElementById("album_control_modal").getAttribute("data-target_album_item_id")
    )
    start_album_id = album_item.getAttribute("data-album_id")
    shuffle_albums = false
    device_play_select()
});

document.getElementById("play_on_selected_device").addEventListener("click", function() {
    var selected_device = device_select.options[device_select.selectedIndex].text
    play_collection(devices[selected_device])
});

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

        var elements = document.getElementsByClassName('complete_album')
        for(var i = 0; i < elements.length; i++) {
            elements[i].style.cursor = "grab"
        }

        var elements = document.getElementsByClassName('album_img')
        for(var i = 0; i < elements.length; i++) {
            element = elements[i]
            if (element.closest('.album_item').classList.contains('complete_album')) {
                element.style.opacity = 0.5
            }
        }

        var elements = document.getElementsByClassName('album-item-move-container')
        for(var i = 0; i < elements.length; i++) {
            element = elements[i]
            if (element.closest('.album_item').classList.contains('complete_album')) {
                element.classList.add('card-img-overlay')
            }
        }

        var elements = document.getElementsByClassName('album-item-move')
        for(var i = 0; i < elements.length; i++) {
            element = elements[i]
            if (element.closest('.album_item').classList.contains('complete_album')) {
                $(element).show()
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
    }
})