define(function () {

    var WebSocketClient = require('websocket.js').default;

    MavErrorMonitor = function (output) {
        var ws = new WebSocketClient('ws://' + window.location.host + '/mavlink/errors/*-*');
        ws.onmessage = function (m) {
            if (output.length > 50) {
                output.splice(0, 1);
            }
            output.push(m.data);
        };
    };

    return MavErrorMonitor;

});