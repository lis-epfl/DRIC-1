define(function () {
    var printf = require('printf');
    var WebSocketClient = require('websocket.js').default;

    var el = '#page-dronekit';

    var app = {
        el: el,
        data: {
            isConnected: false
        },
        methods: {
            buildConnectionString: function (e) {
                var $el = $(el);
                var $output = $el.find('[name="dronekit-connection-string"]');
                var output = '';

                var host = $el.find('[name="host"]').val();
                var port = $el.find('[name="port"]').val();

                switch ($el.find('select').val()) {
                    case 'TCP':
                        output = printf("tcp:%s:%s", host, port)
                        break;
                    case 'UDP':
                        output = printf("%s:%s", host, port)
                        break;
                }

                console.log(output);
                $output.val(output);
            },
            advancedclick: function (e) {
                var $el = $(el);
                var $button = $el.find('.show-advanced-dronekit-connection-string-button');

                var pressed = $button.attr('aria-pressed') === 'true';
                $button.attr('aria-pressed', !pressed ? 'true' : 'false');
                $button.find('i').attr('class', !pressed ? 'fa fa-fw fa-caret-down' : 'fa fa-fw fa-caret-right');
                if (!pressed) {
                    $el.find('.advanced-dronekit-connection-string').slideDown();
                } else {
                    $el.find('.advanced-dronekit-connection-string').slideUp();
                }
            },
            connect: function (e) {
                var self = this;
                var $el = $(el);
                var connectionString = $el.find('[name="dronekit-connection-string"]').val();
                var $box = $('.dronekit-connection-box');

                e.preventDefault();

                $el.find('.dronekit-working').show();
                $el.find('.dronekit-connexion-msg').hide();

                $.post('/dronekit/connect', { ip: connectionString })
                    .done(function () {
                        $box.removeClass('box-danger');
                        $box.addClass('box-success');
                        self.isConnected = true;
                    })
                    .fail(function () {
                        $el.find('.dronekit-connexion-msg-error').show();
                        self.isConnected = false;
                    })
                    .always(function () {
                        $el.find('.dronekit-working').hide();
                    });
            }
        }
    };

    var vehicleStatus = new WebSocketClient('ws://' + window.location.host + '/datasource?s=dronekit-heartbeat', undefined, { strategy: "exponential" });
    vehicleStatus.onmessage = function (m) {
        if (m.data === '___NOVEHICLE__') {
            app.data.isConnected = false;
        } else {
            app.data.isConnected = true;
        }
    };
    vehicleStatus.onclose = function (m) {
        app.data.isConnected = false;
        console.debug('disconnected');
    }

    return app;
});