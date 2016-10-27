define('dric.charts.ControllableAxis', function () {
    var ControllableAxis = function (max, min, getAxis) {
        var _max = max;
        var _min = min

        var self = this;

        self.max = max;
        self.min = min;

        // namespace definition
        this._d = { zoom: {}, pan: {} };

        function multiplyByRatio(ratio) {
            self.max = getAxis().max *= ratio;
            self.min = getAxis().min *= ratio;
        }

        // zoom functions
        this._d.zoom.plus = function () {
            multiplyByRatio(0.9);
        };

        this._d.zoom.minus = function () {
            multiplyByRatio(1.1);
        };

        this._d.zoom.auto = function () {
            self.max = null;
            self.min = null;
        };

        this._d.zoom.mousewheel = function (e) {
            if (e.wheelDelta > 0) {
                self._d.zoom.plus();
            } else if (e.wheelDelta < 0) {
                self._d.zoom.minus();
            }
        };

        this._d.pan.mousedrag = function (e) {
            if (typeof self._d.pan.last === 'undefined') {
                self._d.pan.last = { x: e.x, y: e.y };
                return;
            }
            var delta = (e.y - self._d.pan.last.y) * (getAxis().max - getAxis().min) * 0.005;
            self.max = getAxis().max += delta;
            self.min = getAxis().min += delta;
            self._d.pan.last = { x: e.x, y: e.y };
        };

        this._d.pan.mousedragstop = function () {
            delete self._d.pan.last;
        };

        this._d.force = function (min, max) {
            self.min = getAxis().min = min;
            self.max = getAxis().max = max;
        };
    };

    ControllableAxis.and = function (a, b) {
        return function (e) {
            a(e);
            b(e);
        };
    }

    return ControllableAxis;
});