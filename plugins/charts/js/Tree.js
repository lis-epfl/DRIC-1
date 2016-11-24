define(function () {
    var ColorHelper = require('ColorHelper');
    require('string.prototype.startswith');
    var self = {};

    function downloadDatasourcesList(loaded) {
        $.getJSON('/dsws_datasources', loaded);
    }

    function fireChange(selector, observableTree) {
        var $tree = $(selector);
        if (typeof observableTree.onchange == 'function') {
            observableTree.selection = $tree.treeview('getSelected').map(function (node) {
                return node.source;
            });
            observableTree.onchange.call(observableTree);
        }
    }


    function makeFromData(selector, list, observableTree) {
        var $tree = $(selector);
        var data = formatData(list);

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
                fireChange(selector, observableTree);
            })
            .on('nodeUnselected', function (event, node) {
                node.$el.css('background', '');
                fireChange(selector, observableTree);
            });

        observableTree.getColorForSource = function (source) {
                var selected = $tree.treeview('getSelected');
                for (var i = 0; i < selected.length; i++) {
                    if (selected[i].source === source) {
                        return selected[i].$el.css('background-color');
                    }
                }
            
        };
        $tree.treeview('collapseAll', { silent: true });
    }

    function clear(selector) {
        var $tree = $(selector);
        var selected = $tree.treeview('getSelected');
        for (var i = 0; i < selected.length; i++) {
            $tree.treeview('unselectNode', selected[i]);
        }
    }

    self.make = function (selector) {
        var observableTree = {
            onchange: null,
            selection: null,
            colorProvider: null,
            clear: function () { clear(selector); }
        };

        $('.refresh-chart-source-tree-button').on('click', function () {
            downloadDatasourcesList(function (json) {
                makeFromData(selector, json, observableTree);
                fireChange(selector, observableTree);
            });
        });
        $('.search-chart-source-tree').on('keyup', function () {
            var $searchinput = $('.search-chart-source-tree');
            var $tree = $(selector);

            var query = $searchinput.val();
            
            $tree.treeview('clearSearch');
            $tree.treeview('collapseAll', { silent: true });
            if (query.length > 0) {
                $tree.treeview('search', query);
                $tree.find('.node-:not(.node-result)').css('display', 'none');
                $tree.find('.node-.node-result')
                    .css('display', '')
                    .each(function (i, e) {
                        var nodeId = $(e).attr('data-nodeid');
                        $tree.find('.node-').filter(function () {
                            var id = $(this).attr('data-nodeid');
                            return nodeId.startsWith(id + '.') || id.startsWith(nodeId + '.');
                        }).css('display', '');
                    });
            } else {
                $tree.find('.node-').css('display', '');
            }
        });

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