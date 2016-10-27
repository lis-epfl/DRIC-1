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

	$(function () {
	    __webpack_require__(1);
	});

/***/ },
/* 1 */
/***/ function(module, exports, __webpack_require__) {

	var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function () {
	    // Add menu item
	    $.get("/content/core/devtools/templates/menu_item.mustache", function (template) {
	        var view = {
	            i: function () {
	                return function (text, render) {
	                    return render(text);
	                }
	            }
	        };
	        var menuItem = Mustache.render(template, view);
	        $('ul.sidebar-menu').append(menuItem);
	    });

	    // Add page page-develtools
	    $.get("/content/core/devtools/templates/page-devtools.mustache", function (template) {
	        $.getJSON("/devtools/plugins", function (data) {
	            var view = {
	                plugins: data.sort().map(function (e) {
	                    return { name: e };
	                })
	            };
	            var page = Mustache.render(template, view);
	            $('.content-wrapper').append(page);
	        });

	    });

	    // Create box manager
	    dric.box.devtools = new dric.BoxManager('.devtools-boxes');

	    // Add box
	    var boxRestart = new dric.Box()
	        .setTitle('Developer tools');
	}.call(exports, __webpack_require__, exports, module), __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }
/******/ ]);