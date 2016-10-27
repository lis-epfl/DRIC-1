define(function () {
    var WebSocketClient = require('websocket.js').default;
    var CircularBuffer = require('circular-buffer');

    var observable = {
        onUpdate: null
    };

    var messagesCountWs = new WebSocketClient('ws://' + window.location.host + '/datasource?s=mavlink/messages_count', undefined, { strategy: 'exponential' });

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

    return observable;
});