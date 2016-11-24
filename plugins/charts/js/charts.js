require("bootstrap-treeview/bootstrap-treeview.min.js");

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
            var Plot = require('Plot');
            var plotRegistry = Plot.make('#samples-chart');

            var Tree = require('Tree');
            var observableTree = Tree.make('.chart-source-tree');

            observableTree.onchange = function () {
                plotRegistry.update(this.selection);
            };
            plotRegistry.colorProvider = observableTree;
            plotRegistry.clear = observableTree.clear;
        });
    });
}

samplesCharts();
