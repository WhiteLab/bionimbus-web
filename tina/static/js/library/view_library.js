/**
 * Created by dfitzgerald on 7/18/17.
 */
var socket = new WebSocket('ws://' + window.location.host + '/cart/');
socket.onmessage = function(e) {
    console.log('got message from server');
    var serverMessage = JSON.parse(e.data);
    if (serverMessage.success) {
        if (serverMessage.cartSize > 0) {
            $('#cart-size').removeClass('hidden').text(serverMessage.cartSize);
        }
    } //else {
    //     makeToast({text: msg.information});
    // }
    if (serverMessage.action === 'toast') {
        makeToast({text: serverMessage.content});
    }
};

var sendSocketMessage = function(socketMessage) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(socketMessage));
    } else {
        // TODO Try implementing ReconnectingSocket, which would make this obsolete
        makeToast({text: 'The application lost connection to the server, ' +
                         'please refresh and try again.'});
    }
};

$(document).ready(function(){
    $('span.library-button').click(sendSocketMessage);

    $('#tina-groupby').change(function(){
        window.location.href = window.location.origin + window.location.pathname + '?group_by=' + $(this).val();
    });

    $('#tina-add-to-cart-btn').click(function() {
        var libPrimaryKeys = [];
        var $checkedLibs = $('.tina-small-check:checked').each(function() {
            libPrimaryKeys.push(parseInt($(this).data('lib-pk')));
            $(this).prop('checked', false);
        });
        if (libPrimaryKeys.length > 0){
            var socketMessage = {
                library_pks: libPrimaryKeys
            };
            sendSocketMessage(socketMessage);
        } else {
            makeToast({text: 'No libraries were selected.'})
        }

    });

    // var rows = [
    //     ['a', 'b', 'c', 'd'],
    //     ['e', 'f', 'g', 'h'],
    //     ['i', 'j', 'k', 'l']
    // ];
    //
    // new ATable({
    //     el: '#atable',
    //     dataFunction: function(atable) {atable.receivedData(rows)},
    //     columns: [
    //         {name: 'one', label: 'One'},
    //         {name: 'two', label: 'Two'},
    //         {name: 'three', label: 'Three'},
    //         {name: 'four', label: 'Four'}
    //     ],
    //     height: 200
    // }).render();
});