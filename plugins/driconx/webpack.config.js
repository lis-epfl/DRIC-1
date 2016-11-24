var path = require('path');

module.exports = {
    entry: './js/driconx-main.js',
    output: {
        path: './dist',
        filename: 'driconx.js'
    },
    resolve: {
        root: [
            path.resolve('.'),
            path.resolve('./js')
        ]
    }
};