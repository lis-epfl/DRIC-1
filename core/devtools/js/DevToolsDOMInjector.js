define(function () {
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
});