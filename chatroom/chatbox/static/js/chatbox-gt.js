$(document).ready(function() {
    var grid = $('#posts-window');
    grid.masonry({
        itemSelector: '.grid-item',
    })

    grid.removeClass('invisible');
});