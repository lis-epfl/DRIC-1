define(function () {

    var FixedLengthAxis = function (lengthProvider, maxProvider) {
        this.mode = 'time';
        this.minTickSize = [1, 'second'];
        this.tickSize = [5, 'second'];

        this.update = function() {
            var max = maxProvider();
            var length = lengthProvider();

            this.max = max;
            this.min = max - length;

        }
        this.update();
    };

    return FixedLengthAxis;
});