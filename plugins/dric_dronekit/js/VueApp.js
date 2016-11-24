define(function () {
    var printf = require('printf');
    var WebSocketClient = require('websocket.js').default;
    var WebSocketDatasource = require('websocketdatasource');

    var el = '#page-dronekit';

    function updateIndicator(color, removeOrange) {
        var $indicator = $('.dronekit-indicator');
        $indicator.removeClass('connecting-red connecting-green');
        if(removeOrange)
            $indicator.removeClass('connecting-orange');
        $indicator.addClass('connecting-' + color);
    }

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
                updateIndicator('orange');

                $.post('/dronekit/connect', { ip: connectionString })
                    .done(function () {
                        $box.removeClass('box-danger');
                        $box.addClass('box-success');
                        updateIndicator('green', true);
                        self.isConnected = true;
                    })
                    .fail(function () {
                        $el.find('.dronekit-connexion-msg-error').show();
                        updateIndicator('red', true);
                        self.isConnected = false;
                    })
                    .always(function () {
                        $el.find('.dronekit-working').hide();
                    });
            }
        }
    };

    var vehicleStatus = new WebSocketDatasource('ws://' + window.location.host + '/datasource?s=dronekit-heartbeat');
    vehicleStatus.onmessage = function (m) {
        if (m.data === '___NOVEHICLE__') {
            updateIndicator('red');
            app.data.isConnected = false;
        } else {
            updateIndicator('green');
            app.data.isConnected = true;
        }
    };
    vehicleStatus.onclose = function (m) {
        updateIndicator('red');
        app.data.isConnected = false;
        console.debug('disconnected');
    }

    //var vehicleStatus = new WebSocketClient('ws://' + window.location.host + '/datasource?s=dronekit-heartbeat', { strategy: "exponential" });
    //vehicleStatus.onmessage = function (m) {
    //    if (m.data === '___NOVEHICLE__') {
    //        updateIndicator('red');
    //        app.data.isConnected = false;
    //    } else {
    //        updateIndicator('green');
    //        app.data.isConnected = true;
    //    }
    //};
    //vehicleStatus.onclose = function (m) {
    //    updateIndicator('red');
    //    app.data.isConnected = false;
    //    console.debug('disconnected');
    //}

    return app;
});