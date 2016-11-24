define(function () {
    var WebSocketDatasource = require('websocketdatasource');

    var BatteryUpdater = function (battery) {

        this.updateESID = function (esid) {
            function helper(source, handler) {
                var ws = new WebSocketDatasource('ws://' + window.location.host + '/datasource?s=' + source);
                ws.onmessage = function (m) {
                    var view = new DataView(m.data);
                    var value = view.getFloat64(8);
                    handler(value);
                };
            }

            helper('mavlink-SYS_STATUS/battery_remaining$' + esid,
                function (v) { battery.charge = v; });
            helper('mavlink-SYS_STATUS/current_battery$' + esid,
                function (v) { battery.current = v; });
            helper('mavlink-SYS_STATUS/voltage_battery$' + esid,
                function (v) { battery.tension = v; });
        }
    };
    return BatteryUpdater;
});