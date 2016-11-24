define(function () {
    var WebSocketDatasource = require('websocketdatasource');
    var CircularBuffer = require('circular-buffer');

    var observable = {
        onUpdate: null,
        updateESID: function (newesid) {
            esid = newesid;
            update(esid);
        }
    };

    function update(esid) {
        var messagesCountWs = new WebSocketDatasource('ws://' + window.location.host + '/datasource?s=mavlink/messages_count$' + esid, undefined, { strategy: 'exponential' });

        var last = -1;
        var diffBuffer = new CircularBuffer(5);



        messagesCountWs.onopen = function () {
            messagesCountWs.binaryType = 'arraybuffer';
        }
        messagesCountWs.onmessage = function (m) {
            var view = new DataView(m.data);
            var time = view.getFloat64(0);
            var count = view.getFloat64(8);


            var diff = count - last;
            diffBuffer.enq({ time: time, diff: diff, count: count });
            last = count;
            var from = diffBuffer.get(diffBuffer.size() - 1);
            var to = diffBuffer.get(0);
            var rate = Math.round((to.count - from.count) / (to.time - from.time));

            if (typeof observable.onUpdate === 'function') {
                observable.onUpdate({
                    rate: rate,
                    total: count,
                    progress: rate
                });
            }
        };
    }
    return observable;
});