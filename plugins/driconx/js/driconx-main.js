define(function () {

    var vueApp = require('VueApp'); 

    $.get('/content/plugins/driconx/templates/menuitem_driconx.mustache', function (template) {
        $('.sidebar-menu').append(template);
    });

    $.get('/content/plugins/driconx/templates/driconx.mustache', function (template) {
        $('.content-wrapper').append(template);
        vueApp("#page-connections");
    });

});