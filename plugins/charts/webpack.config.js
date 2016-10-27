var path = require('path');

module.exports = {
    entry: './js/charts.js',
    output: {
        path: './js',
        filename: 'bundle-charts.js'
    },
    resolve: {
        root: [
            path.resolve('.'),
            path.resolve('./js')
        ],
        alias: {
            'bootstrap-treeview': 'bootstrap-treeview/dist'
        }
    },
    loaders: [{
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
    }]
};