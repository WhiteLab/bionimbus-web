/**
 * Created by dfitzgerald on 7/18/17.
 */
var socket = new WebSocket('ws://' + window.location.host + '/cart/');
socket.onmessage = function(e) {
    console.log('got message from server');
    var msg = JSON.parse(e.data);
    if (msg.success) {
        if (msg.cartSize > 0) {
            $('#cart-size').removeClass('hidden').text(msg.cartSize);
        }
    } else {
        makeToast({text: msg.information});
    }
};

$(document).ready(function(){
    $('span.library-button').click(function(){
        if (socket.readyState === WebSocket.OPEN) {
            var pk = parseInt($(this).data('pk'));
            socket.send(JSON.stringify({library_pk: pk}));
        } else {
            // TODO Try implementing ReconnectingSocket, which would make this obsolete
            makeToast({text: 'The application lost connection to the server, ' +
                             'please refresh and try again.'});
        }

    });
});