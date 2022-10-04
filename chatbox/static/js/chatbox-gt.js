$(document).ready(function() {
    var grid = $('#posts-window');
    grid.masonry({
        itemSelector: '.grid-item',
    })

    grid.removeClass('invisible');

    $('.grid-item.image-post').mouseenter(function() {
        var overlayTop = $(this).children('.grid-item-content-wrapper').children('.grid-item-overlay.top');
        var overlayBottom = $(this).children('.grid-item-content-wrapper').children('.grid-item-overlay.bottom');

        overlayTop.addClass('show');
        overlayBottom.addClass('show');
    });

    $('.grid-item').mouseleave(function() {
        var overlays = $(this).children('.grid-item-content-wrapper').children('.grid-item-overlay');
        overlays.removeClass('show');
    });
});