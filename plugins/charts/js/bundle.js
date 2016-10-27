/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
	    function samplesCharts() {
	        //We create the box with the dric Box helper
	        var box = new dric.Box();
	        box.setTitle('Sample-plot');
	        box.setCloseable(true);
	        box.setCollapsable(true);
	        $.get('/content/plugins/charts/templates/chart.mustache', function (template) {
	            box.setContent(template);

	            //Append the box to the home page
	            dric.box.home.append(box, function () {

	                var ControllableAxis = function (max, min) {
	                    var _max = max;
	                    var _min = min;

	                    var self = this;

	                    // namespace definition
	                    this._d = { zoom: {} };

	                    // zoom functions
	                    this._d.zoom.plus = function () {
	                        self.max = _max *= 0.9;
	                        self.min = _min *= 0.9;
	                    }

	                    this._d.zoom.minus = function () {
	                        var ratio = 1.1;
	                        self.max = _max *= ratio;
	                        self.min = _min *= ratio;
	                    }

	                    this._d.zoom.auto = function () {
	                        self.max = null;
	                        self.min = null;
	                    }
	                };

	                var options = {
	                    yaxis: new ControllableAxis(1.5, -1.5),
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

	                redraw();

	                function redraw() {
	                    if (!paused) {
	                        $.plot($("#samples-chart"), [rng.res, sin.res], options);
	                    }

	                    setTimeout(redraw, 70);
	                }

	                var vappCharts = new Vue({
	                    el: '#vapp-charts',
	                    methods: {
	                        pause: function () {
	                            paused = !paused;
	                        },
	                        startRecord: function () { },
	                        zoomAuto: options.yaxis._d.zoom.auto,
	                        zoomPlus: options.yaxis._d.zoom.plus,
	                        zoomMinus: options.yaxis._d.zoom.minus
	                    }
	                });
	            });
	        });

	        /************************************
	        * REAL TIME PLOT UPDATE             *
	        *************************************/
	        var paused = false;
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
	                    var split = this.result.split(' ');
	                    var time = parseFloat(split[0]);
	                    var mag = parseFloat(split[1]);
	                    update(time, mag);
	                };
	                filereader.readAsBinaryString(msg.data);
	            }

	            function update(time, mag) {
	                if (self.res.length > max_point) {
	                    self.res = self.res.slice(1);
	                }
	                self.res.push([time, mag]);
	            }

	            function request() {
	                if (socket !== null && socket.readyState === WebSocket.OPEN) {
	                }
	            }
	        }
	    }

	    samplesCharts();
	}.call(exports, __webpack_require__, exports, module), __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));


/***/ }
/******/ ]);