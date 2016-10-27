define(function () {
    var ControllableAxis = require('ControllableAxis');
    var randomstring = require('randomstring');
    var self = {};
    var sid = randomstring.generate();

    function PlotRegistry() {
        var host = window.location.host;
        var templateUrl = 'ws://' + host + '/datasource?s=__SOURCE__&p=10&sid=' + sid;
        var sources = {};
        var colors = [];
        var colorsValid = false;
        var self = this;

        this.colorProvider = null;
        this.visiblePoints = 300;
        this.offset = 0;

        this.getColors = function () {
            if (!colorsValid) {
                if (this.colorProvider !== null) {
                    colors = [];
                    for (source in sources) {
                        colors.push(this.colorProvider.getColorForSource(source));
                    }
                    colorsValid = true;
                }
                console.log(colors);
            }
            return colors;
        }

        this.update = function (updatedSources) {
            // Delete open sources which are not in updated sources
            for (source in sources) {
                if (updatedSources.indexOf(source) < 0) {
                    sources[source].close();
                    delete sources[source];
                    invalidate();
                }
            }

            // Add updates sources which are not in open sources
            for (var i = 0; i < updatedSources.length; i++) {
                var source = updatedSources[i];
                if (!(source in sources)) {
                    var url = templateUrl.replace('__SOURCE__', source);
                    sources[source] = new RealTimePlotUpdate(url, 300);
                    invalidate();
                }
            }
        };

        this._pause_start = function () {
            var i = 0;
            var forcedStart = [];
            for (source in sources) {
                var res = sources[source].res;
                forcedStart[i] = {};
                forcedStart[i].start = Math.max(res.length - self.visiblePoints - self.offset, 0);
                forcedStart[i].end = Math.min(forcedStart[i].start + self.visiblePoints, res.length);
                console.log('**************************', forcedStart[i]);
                i++;
            }
            return forcedStart;
        };

        this._plotdata = function (forced) {
            var data = [];
            var i = 0;
            for (source in sources) {
                var res = sources[source].res;
                var start = Math.max((typeof forced === 'undefined' ? Math.max(res.length - self.visiblePoints, 0) : forced[i].start) - self.offset, 0);
                var end = Math.min(typeof forced === 'undefined' ? (start + self.visiblePoints) : forced[i].end - self.offset, res.length, res.length);
                console.log((typeof forced === 'undefined' ?'' :forced[i].start));
                data.push(res.slice(start, end));
                i++;
            }
            return data;
        };

        function invalidate() {
            colorsValid = false;
        }
    }

    function RealTimePlotUpdate(url, max_point) {
        var data = [];
        var socket = null;
        this.res = [];
        var self = this;
        open_socket();

        function open_socket() {
            socket = new WebSocket(url);
            socket.onmessage = recv;
            socket.onopen = request;
            socket.binaryType = 'arraybuffer';
        }

        function recv(msg) {
            var view = new DataView(msg.data);
            for (var i = 0; i < view.byteLength; i += 16) {
                var time = view.getFloat64(i);
                var mag = view.getFloat64(i + 8);
                update(time, mag);
            }
            //var filereader = new FileReader();
            //filereader.onload = function () {
            //    var split = this.result.split(' ');
            //    var time = parseFloat(split[0]);
            //    var mag = parseFloat(split[1]);
            //    update(time, mag);
            //};
            //filereader.readAsBinaryString(msg.data);
        }

        function update(time, mag) {
            //if (self.res.length > max_point) {
            //    self.res = self.res.slice(1);
            //}
            self.res.push([time, mag]);
        }

        function request() {
            if (socket !== null && socket.readyState === WebSocket.OPEN) {
            }
        }

        this.close = function () {
            socket.close();
        }
    }

    self.make = function (selector) {
        var plotRegistry = new PlotRegistry();
        var options = {
            yaxis: new ControllableAxis(1.5, -1.5, function () { return plot !== null ? plot.getYAxes()[0] : { min: 0, max: 0 }; }),
            xaxis: new ControllableAxis(null, null, function () { return plot !== null ? plot.getXAxes()[0] : { min: 0, max: 0 }; })
        };


        //var rng = new RealTimePlotUpdate('ws://' + host + '/datasource?s=Samples/rng&p=17', 300);
        //var sin = new RealTimePlotUpdate('ws://' + host + '/datasource?s=Samples/sin&p=28', 300 / 28 * 17);

        var pauseData = [];
        var plot = null;

        redraw();

        /**
        Return range of data in the given dimension.
        Return {min: min, max: max};
        */
        function rangeOf(data, dimension) {
            var range = { min: null, max: null };
            for (var serieIndex = 0; serieIndex < data.length; serieIndex++) {
                var serie = data[serieIndex];
                for (var pointIndex = 0; pointIndex < serie.length; pointIndex++) {
                    var point = serie[pointIndex];
                    if (range.min == null) {
                        range.min = point[dimension];
                    } else if (point[dimension] < range.min) {
                        range.min = point[dimension];
                    }
                    if (range.max == null) {
                        range.max = point[dimension];
                    } else if (point[dimension] > range.max) {
                        range.max = point[dimension];
                    }
                }
            }
            return range;
        }
        var pauseStart;
        function redraw() {
            var plotdata;
            var xrange;

            if (paused) {
                plotdata = plotRegistry._plotdata(pauseStart);
            } else {
                plotdata = plotRegistry._plotdata();
            }

            xrange = rangeOf(plotdata, 0);
            //options.xaxis._d.force(xrange.min, xrange.max);
            options.colors = plotRegistry.getColors();

            plot = $.plot($(selector), plotdata, options);

            // Animation frame won't work here
            setTimeout(redraw, 70);
        }

        function copyRealtime() {
            var data = plotRegistry._plotdata();
            pauseData = [];
            for (var i = 0; i < data.length; i++) {
                pauseData.push(data[i].slice(0));
            }
            pauseStart = plotRegistry._pause_start();
        }

        var lastxdrag = null;
        function xmousedrag(e) {
            if (lastxdrag === null) {
                lastxdrag = { x: e.x, y: e.y };
                return;
            }

            var delta = (e.x - lastxdrag.x) * 0.01;
            plotRegistry.offset = Math.max(plotRegistry.offset + delta, 0);
            console.debug(plotRegistry.offset);
        }

        var vappCharts = new Vue({
            el: '#vapp-charts',
            data: {
                cursor: 'default',
                mousedown: false
            },
            methods: {
                pause: function (e) {
                    paused = !paused;
                    copyRealtime();
                },
                startRecord: function () { },
                pan: function (e) {
                    if (this.mouseButtonDown) {
                        this.cursor = 'all-scroll';
                        options.yaxis._d.pan.mousedrag(e);
                        xmousedrag(e);
                    } else {
                        this.cursor = 'default';
                    }
                },
                zoomAuto: options.yaxis._d.zoom.auto,
                zoomPlus: options.yaxis._d.zoom.plus,
                zoomMinus: options.yaxis._d.zoom.minus,
                zoom: options.yaxis._d.zoom.mousewheel,
                mousedown: function (e) { e.preventDefault(); this.mouseButtonDown = true; },
                mouseup: function (e) {
                    e.preventDefault(); this.mouseButtonDown = false;
                    options.yaxis._d.pan.mousedragstop();
                    lastxdrag = null;
                }
            }
        });

        /************************************
        * REAL TIME PLOT UPDATE             *
        *************************************/
        var paused = false;
        var origin_date = Date.now();
        return plotRegistry;
    }


    return self;
});