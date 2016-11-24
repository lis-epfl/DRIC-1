function dricNetwork() {
    if (typeof dric === 'undefined') {
        dric = new Object();
    }

    var me = {};

    //Create the network global
    dric.network = {};
    //dric.ready('network');

    //Generate a random client identifier (cid)
    //var cid = (Math.random().toString(36)
    //    + Math.random().toString(36)).split('0.').join('');

    //Initialize the box with the box helper
    networkBox = new dric.Box();
    networkBox.setTitle('Network informations');
    networkBox.setCloseable(true);
    networkBox.setCollapsable(true);
    networkBox.setCollapsed(false);

    //Retrieve content and infos
    $.when($.get('/templates/dricnetworkbox.mustache'), $.getJSON('/network/ip'))
        .done(function (d1, d2) {
            var ip = d2[0].ip;
            var content = Mustache.render(d1[0], {
                ip: ip
            });

            networkBox.setContent(content);

            //Update network global
            dric.network.ip = ip;
            //dric.ready('network.ip');

            // Append box on home screen
            dric.box.net.append(networkBox, networkBoxRendered);
        });

    //Callback called once the box template is loaded
    function networkBoxRendered() {
        //The websocket
        var ws = new WebSocket('ws://' + window.location.host + '/network/ws');
        ws.onclose = function () {
            console.log('Disconnected!');
        }

        ws.onmessage = function (message) {
            var filereader = new FileReader();
            filereader.onload = function () {
                var msg = this.result;
                switch (msg.toString().charAt(0)) {
                    case 'Y':
                        me = JSON.parse(msg.substring(1));
                        break;
                    default:
                        updateNetworkInfos();
                }
            };
            filereader.readAsBinaryString(message.data);
        }


        //Refresh button
        $('#network-refresh').click(function () {
            var btn = $(this);
            var icon = $(this).find('i');
            icon.addClass('fa-spin');
            btn.attr('disabled', 'disabled');
            updateNetworkInfos(function () {
                icon.removeClass('fa-spin');
                btn.removeAttr('disabled');
                $("#network-refresh-message")
                        .addClass('text-success')
                        .html("<i class='fa fa-smile-o'></i> Done!");
            }, function () {
                icon.removeClass('fa-spin');
                btn.removeAttr('disabled');
                $("#network-refresh-message")
                        .addClass('text-danger')
                        .html("<i class='fa fa-frown-o'></i> Could not connect to server");
            });
        });
    }


    function updateNetworkInfos(success_cb, fail_cb) {
        $.getJSON('/network/clients', function (clients) {
            //var clients = d1[0];
            //var me = d2[0];
            $('.network tbody').html('');
            clients.sort(function (a, b) {
                return (a.name > b.name);
            });
            for (var i = 0; i < clients.length; i++) {
                var name = clients[i].name;
                var ip = clients[i].ip;
                if ('name' in me && name === me.name) {
                    name += '*';
                }
                var row = $('<tr>')
                        .append('<td>' + ip + '</td>')
                        .append('<td>' + name + '</td>');

                $('.network tbody').append(row);
            }
            //Callback
            if (typeof success_cb === 'function') {
                success_cb();
            }
        }, function () {
            if (typeof fail_cb === 'function') {
                fail_cb();
            }
        });
    }
}
dricNetwork();