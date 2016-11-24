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

	'use strict';

	__webpack_require__(1);

	if (typeof window.dric === 'undefined') {
	    window.dric = new function () {
	        var listeners = [];
	        var fired = [];
	        this.ready = function (component, cb) {
	            if (typeof cb === "undefined") {
	                fire_ready(component);
	            } else {
	                if ($.inArray(component, fired) > -1) {
	                    cb(component);
	                } else {
	                    add_cb(component, cb);
	                }
	            }
	            function add_cb(component, cb) {
	                if (!(component in listeners)) {
	                    listeners[component] = [cb];
	                } else {
	                    listeners[component].push(cb);
	                }
	            }

	            function fire_ready(component) {
	                if (component in listeners) {
	                    var cbs = listeners[component];
	                    if (typeof cbs !== 'undefined') {
	                        for (var i = 0; i < cbs.length; i++) {
	                            cbs[i](component);
	                        }
	                    }
	                }
	                fired.push(component);
	            }
	        };
	    }();
	}

	window.dric.Box = function () {
	    var title = 'Untitled box';
	    var closeable = false;
	    var collapsable = false;
	    var collapsed = false;
	    var content = '';

	    var self = this;

	    this.setTitle = function (newTitle) {
	        title = newTitle;
	        return self;
	    };
	    this.setCloseable = function (isCloseable) {
	        closeable = isCloseable;
	        return self;
	    };
	    this.setCollapsable = function (isCollapsable) {
	        collapsable = isCollapsable;
	        return self;
	    };
	    this.setCollapsed = function (isCollapsed) {
	        collapsed = isCollapsed;
	        return self;
	    };
	    this.setContent = function (newContent) {
	        content = newContent;
	        return self;
	    };
	    this.renderInside = function (target, cb) {
	        $.get('./templates/box.mustache', function (template) {
	            var rendered = Mustache.render(template, {
	                title: title,
	                collapsable: collapsable,
	                closeable: closeable,
	                content: content
	            });
	            $(target).html(rendered);
	            if (typeof cb === 'function') {
	                cb();
	            }
	        });
	    };
	};

	window.dric.BoxManager = function (rowSelector) {
	    var boxes = [];

	    this.append = function (box, callback) {
	        boxes.push(box);

	        box.renderInside($('<div>', { class: 'col-md-12' }).appendTo(rowSelector), callback);
	    };
	};

/***/ },
/* 1 */
/***/ function(module, exports, __webpack_require__) {

	var __WEBPACK_AMD_DEFINE_RESULT__;'use strict';

	!(__WEBPACK_AMD_DEFINE_RESULT__ = function () {

	    isUpData = { isUp: true };
	    var dricofflineLogoindic = {
	        template: '<a href="/" class="logo" v-on:down="alert();isUp=false" v-on:up="alert();isUp=true">' + '<img src="/content/core/index/img/dric.png" style="height:50%;margin:auto;top:25%;position:relative;" class="logo-mini" v-show="isUp">' + '<i class="fa fa-exclamation-circle connecting-orange blink " title="You are disconnected" v-cloak v-show="!isUp"></i>' + '</a>',
	        data: function data() {
	            return isUpData;
	        }
	    };

	    vapp = new Vue({
	        el: '.main-header',
	        components: {
	            'dricoffline-logoindic': dricofflineLogoindic
	        }
	    });

	    function setUp(up) {
	        isUpData.isUp = up;
	    }

	    setInterval(function () {
	        var xhr = new XMLHttpRequest();
	        xhr.open('HEAD', '/');
	        xhr.timeout = 1000;
	        xhr.onload = function () {
	            setUp(true);
	        };
	        xhr.ontimeout = function () {
	            setUp(false);
	        };
	        xhr.send();
	    }, 1000);
	}.call(exports, __webpack_require__, exports, module), __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }
/******/ ]);