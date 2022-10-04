function urlize(inputText) {
    var replacedText, replacePattern1, replacePattern2, replacePattern3;

    //URLs starting with http://, https://, or ftp://
    replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
    replacedText = inputText.replace(replacePattern1, '<a href="$1" target="_blank">$1</a>');

    //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
    replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    replacedText = replacedText.replace(replacePattern2, '$1<a href="http://$2" target="_blank">$2</a>');

    //Change email addresses to mailto:: links.
    replacePattern3 = /(([a-zA-Z0-9\-\_\.])+@[a-zA-Z\_]+?(\.[a-zA-Z]{2,6})+)/gim;
    replacedText = replacedText.replace(replacePattern3, '<a href="mailto:$1">$1</a>');

    return replacedText;
}

function subscribe(url) {
    $.ajax({
        url: url,
        method: "post",
        data: {
            csrfmiddlewaretoken: Cookies.get('csrftoken'),
            function: 'subscribe',
        },
        success: function(data) {
            var subbed = data.subscribed;

            if (subbed) {
                $("#sub-button").removeClass("not-subbed");
                $("#sub-button").addClass("subbed");
                $("#sub-button").text('Unsubscribe');
            } else {
                $("#sub-button").removeClass("subbed");
                $("#sub-button").addClass("not-subbed");
                $("#sub-button").text('Subscribe');
            }
        }
    });
}

function constructAuthModal(modal, response) {
    R = $(response);
    modalWrapper = $('<div/>', {
        class: 'modal-content px-5 py-3',
    }).appendTo(modal.children('.modal-dialog'));
    
    title = R.find('#title').text();
    titleDiv = $('<div/>', {
        class: 'modal-header',
    }).appendTo(modalWrapper);
    
    titleHeader = $('<h5/>', {
        class: 'modal-title text-dark',
        text: title,
    }).appendTo(titleDiv);

    /*exitButton = $('<button/>', {
        class: 'close',
    }).appendTo(titleDiv);*/

    form = R.find('form');
    formTexts = form.find('.text-light')
    formTexts.each(function(index, obj) {
        $(obj).removeClass('text-light');
        $(obj).addClass('text-dark');
    });

    form.appendTo(modalWrapper);
}

function constructDeleteModal(modal, response) {
    R = $(response);

    modalWrapper = $('<div/>', {
        class: 'modal-content px-5 py-3',
    }).appendTo(modal.children('.modal-dialog'));
    
    title = R.find('#title').text();
    titleDiv = $('<div/>', {
        class: 'modal-header',
    }).appendTo(modalWrapper);
    
    titleHeader = $('<h5/>', {
        class: 'modal-title text-dark',
        text: title,
    }).appendTo(titleDiv);

    confirmText = R.find('#confirm-text').text;
    
    form = R.find('form');
    form.find('#confirm-text').removeClass('display-5').removeClass('my-5').addClass('text-dark').addClass('my-3');
    form.appendTo(modalWrapper);

    nobutton = form.find('#nobutton');
    nobuttonlink = nobutton.parent();

    nobutton.appendTo(form.find('#selections'));
    nobuttonlink.remove();
}

function constructModal(modal, response) {
    // R = $.parseHTML(response);
    var parser = new DOMParser();
    var doc = parser.parseFromString(response, "text/html");
    var modalType = doc.querySelector('meta[name="modal-type"]')['content'];

    switch (modalType) {
        case 'delete':
        constructDeleteModal(modal, response); break;
        case 'auth':
        constructAuthModal(modal, response); break;
    }
}

$(document).ready(function() {
   
    $('#modal').on('show.bs.modal', function (event) {
        var modal = $(this)
        var button = $(event.relatedTarget)
        var url = button.attr('href');
        $.ajax({
            url: url,
            context: document.body
        }).done(function(response) {
            constructModal(modal,response);
        });
    })

    $('#modal').on('hide.bs.modal', function (event) {
        $('#modal').children('.modal-dialog').empty();
    });

});