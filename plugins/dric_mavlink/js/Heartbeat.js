define(function () {
    var WebSocketDatasource = require('websocketdatasource');

    var Heartbeat = function (heartbeat) {

        var last;
        var STATUS = [
            'UNINIT',
            'BOOT',
            'CALIBRATING',
            'STANDBY',
            'ACTIVE',
            'CRITICAL',
            'EMERGENCY',
            'POWEROFF',
        ];

        var ws = new WebSocketDatasource('ws://' + window.location.host + '/datasource?s=mavlink-HEARTBEAT/system_status');
        ws.onmessage = function (m) {
            var view = new DataView(m.data);
            var time = view.getFloat64(0);
            var value = view.getFloat64(8);

            heartbeat.status = STATUS[value] ? STATUS[value]: 'UNDEFINED';
            heartbeat.last = time - last;

            last = time;
        };


    };
    return Heartbeat;
});