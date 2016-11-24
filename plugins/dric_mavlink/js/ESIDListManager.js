define(function () {
    return function (esidList) {
        var WebSocketClient = require('websocket.js').default;

        var ws = new WebSocketClient('ws://' + window.location.host + '/mavlink/esid/ws', 'AQ');
        ws.onmessage = function (msg) {
            esidList.splice(0);
            Array.prototype.push.apply(esidList, JSON.parse(msg.data));
        };
        ws.onclose = function () {
            esidList.splice(0);
        };
        ws.onopen = function () {
            ws.send('A');
        };
    };
});