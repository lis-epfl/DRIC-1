define(function () {
    var MessageStats = require('MessageStats');
    var MessagesList = require('MessagesList');
    var debounce = require('debounce');
    var JSON5 = require('JSON5');

    var getMessage = debounce(function (type, n, message) {
        $.get('/mavlink/message/' + type + '/' + n, function (data) {
            message.data = JSON5.parse(data);
        });
    }, 500);

    $.get('/content/plugins/dric_mavlink/templates/menuitem_mavlink.mustache', function (template) {
        $('.sidebar-menu').append(template);
    });

    $.get('/content/plugins/dric_mavlink/templates/cmdsend.mustache', function (template) {
        $('.content-wrapper').append(template);
        vapp = new Vue({
            el: '#page-mavlink',
            data: {
                stats: {
                    rate: 0,
                    progress: 0,
                    total: 0
                },
                heartbeat: {
                    frequency: 0,
                    last: 0,
                },
                battery: {
                    tension: 0,
                    charge: 0,
                    current: 0
                },
                activeType: '',
                messages: [],
                inspectedMessages: {}
            },
            methods: {
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
                            console.log(this.activeType, type, type === this.activeType);
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