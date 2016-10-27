define(function () {

    var vueApp = require('VueApp');


    //Inject menu item
    $.get('/content/plugins/dric_dronekit/templates/menuitem_dronekit.mustache', function (template) {
        $('.sidebar-menu').append(template);
    });

    //Inject page
    $.get('/content/plugins/dric_dronekit/templates/dronekit_page.mustache', function (template) {
        $('.content-wrapper').append(template);
        var vapp = new Vue(vueApp);
        vapp.buildConnectionString();
    });
});