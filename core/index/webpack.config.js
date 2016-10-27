var webpack = require('webpack');

module.exports = {
    entry: './box.js',
    output: {
        path: './js',
        filename: 'box1.js'
    },
    resolve: {
        alias: {
            'bootstrap-treeview': 'bootstrap-treeview/dist'
        }
    },
    module: {
        loaders: [{
            test: /\.js$/,
            exclude: /node_modules/,
            loader: 'babel-loader'
        }, {
            test: /\.css$/, loader: "style-loader!css-loader"
        }],
    }
};
