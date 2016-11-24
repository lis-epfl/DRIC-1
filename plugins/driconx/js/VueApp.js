define(function () {
    return function (el) {
        var WebSocketClient = require('websocket.js').default;
        var driconxws = new WebSocketClient('ws://' + window.location.host + '/driconx/ws');

        var app = new Vue({
            el: el,
            data: {
                active_only: true,
                connections: [],
                newConnection: {
                    type: 'UDP',
                    host: '127.0.0.1',
                    port: '14550',
                    binding: '',
                    connected: false,
                    connecting: false,
                    multibinding: false,
                    status: null,
                    systems_last_time: {}
                },
                connected: false,
                bindings: []
            },
            methods: {
                add: function (e) {
                    e.preventDefault();
                    var newConnx = $.extend(true, {}, this.newConnection);
                    this.connections.push(newConnx);
                    this.connect(newConnx);
                },
                deleteConnection: function (connection) {
                    this.connections.splice(this.connections.indexOf(connection), 1);
                },
                connect: function (connection) {
                    connection.connecting = true;
                    $.ajax({
                        url: 'http://' + window.location.host + '/driconx/new',
                        method: 'put',
                        data: JSON.stringify(connection),
                    }).success(function (data, textStatus, jqXHR) {
                        connection.connecting = false;
                        connection.connected = true;
                        connection.status = null;
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        connection.connecting = false;
                        connection.connected = false;
                        connection.status = errorThrown;
                    });
                },
                disconnect: function (connection) {
                    connection.connecting = true;
                    $.ajax({
                        url: 'http://' + window.location.host + '/driconx/disconnect',
                        method: 'post',
                        data: JSON.stringify(connection)
                    }).success(function (data, textStatus, jqXHR) {
                        connection.connecting = false;
                        connection.connected = false;
                        connection.status = null;
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        connection.connecting = false;
                        connection.connected = true;
                        connection.status = errorThrown;
                    });
                }
            }
        });

        driconxws.onmessage = function (event) {
            var data = JSON.parse(event.data);
            app.connected = true;
            app.connections = data;
        };
        driconxws.onclose = function () {
            app.connected = false;
        };

        $.getJSON('/driconx/bindings', function (bindings) {
            app.bindings = bindings;
        });

        return app;
    }
});