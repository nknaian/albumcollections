window.onload = function() {
    $('#index_loading_add_collections').hide()
    $('#index_loading_remove_collections').hide()
    $('#index_content').show()
}

function show_loading_add_collections() {
    $('#addCollections').modal('hide')
    $('#index_content').hide()
    $('#index_loading_add_collections').show()
}

function show_loading_remove_collections() {
    $('#removeCollections').modal('hide')
    $('#index_content').hide()
    $('#index_loading_remove_collections').show()
}
