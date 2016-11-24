var webpack = require('webpack');

module.exports = {
    entry: './box.js',
    output: {
        path: './js',
        filename: 'box1.js'
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
