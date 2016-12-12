
define(function () {
    require('array-remove-if');

    Aggregation = function (esidList, alias) {
        this.reason = null;
        this.systemid = -1;
        this.alias = alias;
        this.esidList = esidList;
    };

    Vue.component('driconx-aggregs', {
        template: require('raw-loader!components/driconx-aggregs.html'),
        props: ['connections'],
        data: function () {
            return {
                'aggregations': [],
                'showNewDrop': false,
                'pruneTimeout': null,
                'aggregateById': true
            };
        },
        watch: {
            'connections': function () {
                this.recomputeAggregations();
            },
            'aggregateById': function () {
                console.log('ok');
                this.recomputeAggregations();
            }
        },
        methods: {
            recomputeAggregations: function () {
                var connections = this.connections;
                // for each system, check if system is already in aggregation
                for (var i = 0; i < connections.length; i++) {
                    var connection = connections[i];
                    for (var j = 0; j < connection.systems.length; j++) {
                        var system = connection.systems[j];
                        var systemAggreg = this.systemAggregation(system);
                        if (systemAggreg === null) {
                            this.aggregations.push(new Aggregation([{ esid: system, connection: connection }], system));
                        } else if (systemAggreg.esidList.findIndex(e=>e.esid === system) === -1) {
                            // remove from all aggregs
                            this.aggregations.map(a=>a.esidList).forEach(l => l.removeIf(e=>e.esid === system));
                            // add to aggreg
                            systemAggreg.esidList.push({ esid: system, connection: connection });
                        }

                        // update systems' connections ref
                        var candidates = Array.prototype.concat.apply([], this.aggregations.map(a=>a.esidList)).filter(s=>s.esid === system);
                        if (candidates.length > 0) {
                            candidates.forEach(c => c.connection = connection);
                        }
                    }
                }

                // remove orphan systems from aggregations with a slight timeout because we want to give the uav a chance to respond
                window.clearTimeout(this.pruntTimeout);
                var self = this;
                this.pruntTimeout = window.setTimeout(function () {
                    self.aggregations.map(a=>a.esidList)
                    .forEach(l =>l.removeIf(e=>
                        Array.prototype.concat.apply([], self.connections.map(c=>c.systems)).filter(s=>s === e.esid).length == 0
                        ));
                }, 1200);
            },
            drop: function (targetAggreg, event) {
                var system = JSON.parse(event.dataTransfer.getData('application/json')).esid;
                var aggreg = this.systemAggregation(system);

                if (aggreg === null) {
                    console.error('Unknown system');
                    return;
                }

                var index = aggreg.esidList.map(x=>x.esid).indexOf(system);
                var detached = aggreg.esidList.splice(index, 1);

                var connection = this.systemConnection(system);

                if (connection === null) {
                    console.error('Unknown system connection');
                    return;
                }
                detached.connection = connection;
                detached.esid = system;

                targetAggreg.esidList.push(detached);
            },
            deaggregate: function (aggreg) {
                for (var i = 0; i < aggreg.esidList.length; i++) {
                    var esid = aggreg.esidList[i];
                    this.aggregations.push(new Aggregation([esid], esid.esid));
                }
                aggreg.esidList.splice(0, aggreg.esidList.length);
            },
            dropOnNew: function (event) {
                var system = JSON.parse(event.dataTransfer.getData('application/json')).esid;
                var aggreg = this.systemAggregation(system);
                if (aggreg === null) {
                    console.error('Unknown system');
                    return;
                }

                var index = aggreg.esidList.map(x=>x.esid).indexOf(system);
                var detached = aggreg.esidList.splice(index, 1);
                this.aggregations.push(new Aggregation(detached, system));
            },
            systemConnection: function (system) {
                // return connection for system
                for (var i = 0; i < this.connections.length; i++) {
                    var connection = this.connections[i];
                    if (connection.systems.indexOf(system) !== -1) {
                        return connection;
                    }
                }
                return null;
            },
            systemAggregation: function (system) {

                function isEqualSystem(aggregateById, a, b) {
                    console.log(
                        aggregateById,
                        a.substring(a.indexOf('-')),
                        b.substring(b.indexOf('-')),
                        a.substring(a.indexOf('-')) === b.substring(b.indexOf('-')));
                    if (aggregateById) {
                        return a.substring(a.indexOf('-')) === b.substring(b.indexOf('-'));
                    } else {
                        return a === b;
                    }
                }

                // return aggregation for system
                for (var k = 0; k < this.aggregations.length; k++) {
                    var aggregation = this.aggregations[k];
                    if (aggregation.esidList.findIndex(e => isEqualSystem(this.aggregateById, e.esid, system)) !== -1) {
                        return this.aggregations[k];
                    }
                }
                return null;
            }
        }
    });

    Vue.component('driconx-aggreg', {
        props: ['esidList', 'alias', 'reason', 'systemid'],
        template: require('raw-loader!components/driconx-aggreg.html'),
        watch: {
            'esidList': function () {
                if (this.esidList.length <= 0) {
                    this.$emit('empty-aggreg');
                }
            }
        }
    });


});
