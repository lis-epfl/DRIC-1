var path = require('path');

module.exports = {
    entry: './js/main.js',
    output: {
        path: './js',
        filename: 'devtools.js'
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