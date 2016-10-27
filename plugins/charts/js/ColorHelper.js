define('dric.charts.ColorHelper', function () {
    var self;
    var colors = [];
    var cursor = 0;
    var self = {};

    // Matlab color set
    colors.push('rgb(63.50%, 07.80%, 18.40%)');
    colors.push('rgb(0%, 44.7%, 74.1%)');
    colors.push('rgb(85%, 32.5%, 9.8%)');
    colors.push('rgb(92.90%, 69.40%, 12.50%)');
    colors.push('rgb(49.40%, 18.40%, 55.60%)');
    colors.push('rgb(46.60%, 67.40%, 18.80%)');
    colors.push('rgb(30.10%, 74.50%, 93.30%)');

    /**
     * Cycle color set
     */
    self.nextColor = function () {
        cursor = cursor + 1;
        if (cursor < 0 || cursor >= colors.length) {
            cursor = 0;
        }
        return colors[cursor];
    };

    return self;
});