define(function () {
    var WebSocketClient = require('websocket.js').default;
    require('dataview-getstring');

    var observable = {
        onUpdate: null
    };

    var last = {};
    var lastTime = 0;

    var updateStatesWs = new WebSocketClient('ws://' + window.location.host + '/datasource?s=mavlink/messages_stats');
    updateStatesWs.onopen = function () { updateStatesWs.binaryType = 'arraybuffer'; };
    updateStatesWs.onmessage = function (m) {
        var view = new DataView(m.data);
        var time = view.getFloat64(0);
        var jsonText = view.getString(8);
        var stats = JSON.parse(jsonText);

        if (typeof observable.onUpdate === 'function') {
            var out = [];
            for (type in stats) {
                var frequency = 0;
                if (type in last) {
                    frequency = Math.round((stats[type] - last[type]) / (time - lastTime));
                }
                out.push({
                    type: type,
                    count: stats[type],
                    frequency: frequency
                });
            }
            observable.onUpdate(out);
        }
        lastTime = time;
        last = stats;
    };
    return observable;
});