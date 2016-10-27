var path = require('path');

module.exports = {
    entry: './js/network_main.js',
    output: {
        path: './js',
        filename: 'network.js'
    },
    resolve: {
        root: [
            path.resolve('.'),
            path.resolve('./js')
        ]
    },
    loaders: [{
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
    }]
};