require('./js/ConnectionAlert.js')

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
    };

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

        box.renderInside($('<div>', {class: 'col-md-12'})
                .appendTo(rowSelector), callback);

    };

};