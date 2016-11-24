define(function () {
    var MessageStats = require('MessageStats');
    var MessagesList = require('MessagesList');
    var BatteryStats = require('BatteryStats');
    var Heartbeat = require('Heartbeat');
    var MavErrorMonitor = require('MavErrorMonitor');
    var ESIDListManager = require('ESIDListManager');
    var debounce = require('debounce');
    var JSON5 = require('JSON5');

    var UNITS = {}, units = {};
    $.getJSON('/mavlink/units', function (distunits) {
        $.extend(true, UNITS, distunits);
        $.extend(true, units, distunits);
    });

    $.get('/content/plugins/dric_mavlink/templates/menuitem_mavlink.mustache', function (template) {
        $('.sidebar-menu').append(template);
    });

    var batteryStats, heartbeat, mavErrorMonitor, eSIDListManager;    

    $.get('/content/plugins/dric_mavlink/templates/cmdsend.mustache', function (template) {
        $('.content-wrapper').append(template);
        var vapp = new Vue({
            el: '#page-mavlink',
            data: {
                esidList: [],
                esid: null,
                searchquery: '',
                stats: {
                    rate: 0,
                    progress: 0,
                    total: 0
                },
                heartbeat: {
                    status: 'UNDEFINED',
                    last: 0,
                },
                battery: {
                    tension: 0,
                    charge: 0,
                    current: 0
                },
                activeType: '',
                messages: [],
                inspectedMessages: {},
                units: units,
                acquisition: 'boot',
                acquisitionIndex: {},
                maverrors: []
            },
            watch: {
                esid: function (newesid) {
                    MessagesList.updateESID(newesid);
                    MessageStats.updateESID(newesid);
                    batteryStats.updateESID(newesid);
                }
            },
            methods: {
                setAcquisitionFrom(when) {
                    this.acquisitionIndex = {};
                    switch (when) {
                        case 'now':
                            for (var i = 0; i < this.messages.length; i++) {
                                this.acquisitionIndex[this.messages[i].type] = this.messages[i].count;
                            }
                            break;
                    }
                },
                getQuantityFor(unit) {
                    for (q in Conversion.quantities) {
                        if (Conversion.quantities[q].indexOf(unit) >= 0) {
                            return q;
                        }
                    }
                    return null;
                },
                getConvertableUnitsFor(unit) {
                    var quantity = this.getQuantityFor(unit);
                    if (quantity === null) {
                        return null;
                    } else {
                        switch (quantity) {
                            case 'length': return ['nm', 'um', 'mm', 'cm', 'm', 'km'];
                            case 'temperature': return ['°C', '°F'];
                        }
                    }
                },
                convertMavlink: function (type, key, value) {
                    if (type in UNITS && key in UNITS[type] && type in this.units && key in this.units[type]) {
                        var from = UNITS[type][key];
                        var to = this.units[type][key];
                        return Conversion.convert(from, to, value);
                    } else {
                        return value;
                    }
                },
                openMavlinkMsg: function (e) {
                    var $target = $(e.target);
                    var type = $target.attr('data-message-type');
                    this.$set(this.inspectedMessages, type, {
                        type: type,
                        current: 1,
                        count: 1
                    });
                    this.activeType = type;

                    this.inspectedMessages[type].unwatch = this.$watch('inspectedMessages.' + type + '.current',
                        function (newValue, oldValue) {
                            if (type === this.activeType) {
                                getMessage(type, newValue, this.inspectedMessages[type]);
                            }
                        }, { immediate: true });
                },
                closeTab: function (type) {
                    this.inspectedMessages[type].unwatch();
                    delete this.inspectedMessages[type]
                    keys = Object.keys(this.inspectedMessages);
                    this.activeType = keys[keys.length - 1];
                }
            }
        });

        var getMessage = debounce(function (type, n, message) {
            $.get('/mavlink/message/' + vapp.esid + '/' + type + '/' + n, function (data) {
                message.data = JSON.parse(data);
            });
        }, 500);

        batteryStats = new BatteryStats(vapp.battery);
        heartbeat = new Heartbeat(vapp.heartbeat);
        mavErrorMonitor = new MavErrorMonitor(vapp.maverrors);
        eSIDListManager = new ESIDListManager(vapp.esidList);

        MessageStats.onUpdate = function (stats) {
            vapp.stats = stats;
        };

        MessagesList.onUpdate = function (stats) {
            vapp.messages = stats;
            for (var i = 0; i < vapp.messages.length; i++) {
                var type = vapp.messages[i].type;
                if (type in vapp.inspectedMessages) {
                    vapp.inspectedMessages[type].count = vapp.messages[i].count;
                    if (vapp.inspectedMessages[type].auto) {
                        vapp.inspectedMessages[type].current = vapp.inspectedMessages[type].count;
                    }
                }
            }
        };
    });


});