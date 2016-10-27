define(function () {
    var ColorHelper = require('ColorHelper');
    var self = {};

    function downloadDatasourcesList(loaded) {
        $.getJSON('/dsws_datasources', loaded);
    }

    function makeFromData(selector, list, observableTree) {
        var $tree = $(selector);
        var data = formatData(list);

        function fireChange() {
            if (typeof observableTree.onchange == 'function') {
                observableTree.selection = $tree.treeview('getSelected').map(function (node) {
                    return node.source;
                });
                observableTree.onchange.call(observableTree);
            }
        }

        $tree.treeview({
            data: data,
            collapseIcon: "fa fa-chevron-down",
            expandIcon: "fa fa-chevron-right",
            emptyIcon: "fa",
            showBorder: false,
            onhoverColor: "#d9d9d9",
            multiSelect: true
        });
        $tree
            .on('nodeSelected', function (event, node) {
                node.$el.css('background', ColorHelper.nextColor());
                fireChange();
            })
            .on('nodeUnselected', function (event, node) {
                node.$el.css('background', '');
                fireChange();
            });

        observableTree.getColorForSource = function (source) {
                console.log("_>", source);
                var selected = $tree.treeview('getSelected');
                for (var i = 0; i < selected.length; i++) {
                    console.log("%s == %s", selected[i].source, source);
                    if (selected[i].source === source) {
                        return selected[i].$el.css('background-color');
                    }
                }
            
        };
    }

    self.make = function (selector) {
        var observableTree = {
            onchange: null,
            selection: null,
            colorProvider: null
        };
        downloadDatasourcesList(function (json) {
            makeFromData(selector, json, observableTree);
        });
        return observableTree;
    };

    function formatData(list) {
        var data = [];
        var groups = {};

        // First, group sources by category
        for (var i = 0; i < list.length; i++) {
            var split = list[i].split('/');
            var category = split[0];
            var name = split[1];
            if (!(category in groups)) {
                groups[category] = [];
            }
            groups[category].push({ name: name, source: list[i] });
        }

        // Then create the treeview 
        for (category in groups) {
            var nodes = [];
            for (var i = 0; i < groups[category].length; i++) {
                nodes.push({
                    text: groups[category][i].name,
                    icon: 'fa fa-line-chart',
                    source: groups[category][i].source
                });
            }
            data.push({
                text: category,
                selectable: false,
                nodes: nodes
            })
        }
        return data;
    }

    return self;
});