function samplesCharts() {
    //We create the box with the dric Box helper
    var box = new dric.Box();
    box.setTitle('Sample-plot');
    box.setCloseable(true);
    box.setCollapsable(true);
    box.setContent('<div style="width:100%; height:400px" id="samples-chart"></div>');

    //Append the box to the home page
    dric.box.home.append(box, function () {
        var options = {
            yaxis: { max: 1.5, min: -1.5 },
            xaxis: {
                tickFormatter: function (value, axis) {
                    return value / 1000;
                },
                tickSize: 500
            }
        };
        var plot = $.plot($("#samples-chart"), [[]], options);
        var host = window.location.host;
        var rng = new RealTimePlotUpdate('ws://' + host + '/datasource?s=rng&p=17', 200);
        var sin = new RealTimePlotUpdate('ws://' + host + '/datasource?s=sin&p=17', 200);
        //var rng = new RealTimePlotUpdate('ws://' + host + '/samples/charts/ws/rng?p=17', 200);
        //var sin = new RealTimePlotUpdate('ws://' + host + '/samples/charts/ws/sin?p=17', 200);

        redraw();

        function redraw() {
            $.plot($("#samples-chart"), [rng.res, sin.res], options);
            //plot.setData([rng.res, sin.res]);
            //plot.draw();
            setTimeout(redraw, 70);
        }
    });

    /************************************
    * REAL TIME PLOT UPDATE             *
    *************************************/
    var origin_date = Date.now();
    function RealTimePlotUpdate(url, max_point) {
        var data = [];
        var socket = null;
        this.res = [];
        open_socket();
        var self = this;

        function open_socket() {
            socket = new WebSocket(url);
            socket.onmessage = recv;
            socket.onopen = request;
        }

        function recv(msg) {
            var filereader = new FileReader(); 
            filereader.onload = function () {
                update(parseFloat(this.result));
            }; 
            filereader.readAsBinaryString(msg.data);
        }

        function update(n) {
            if (self.res.length > max_point) {
                self.res = self.res.slice(1);
            }
            self.res.push([Date.now() - origin_date, n]);
        }

        function request() {
            if (socket !== null && socket.readyState === WebSocket.OPEN) {             
            }
        }
    }
}

samplesCharts();