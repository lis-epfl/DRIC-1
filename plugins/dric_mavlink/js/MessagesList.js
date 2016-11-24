define(function () {
    var WebSocketDatasource = require('websocketdatasource');
    require('dataview-getstring');

    var esid
    var observable = {
        onUpdate: null,
        updateESID: function (newesid) {
            esid = newesid;
            update(esid);
        }
    };
    function update(esid) {
        var last = {};
        var lastTime = 0;

        var updateStatesWs = new WebSocketDatasource('ws://' + window.location.host + '/datasource?s=mavlink/messages_stats$' + esid);
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
    }
    return observable;
});