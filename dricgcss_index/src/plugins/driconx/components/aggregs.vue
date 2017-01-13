<template>
  <div>
    <div class="checkbox">
      <label>
        <input v-model="aggregateById" type="checkbox"> Aggregate automatically by system id
      </label>
    </div>

    <driconx-aggreg v-for="(aggreg, k) in aggregations"
    :esid-list="aggreg.esidList"
    :alias="aggreg.alias"
    :reason="aggreg.reason"
    :aggreg="aggreg"
    :systemid="aggreg.systemid"
    v-on:alias-changed="aliasChanged(aggreg, $event)"
    v-on:empty-aggreg="emptyAggreg(k, aggreg)"
    v-on:aggreg-drop="drop(aggreg, $event);showNewDrop=false"
    v-on:startdrag="showNewDrop=true"
    v-on:enddrag="showNewDrop=false"
    v-on:deaggregate="deaggregate(aggreg)">
  </driconx-aggreg>

  <div class="box box-primary box-solid"
  v-if="showNewDrop"
  v-on:dragover="$event.preventDefault()"
  v-on:drop="dropOnNew">
  <div class="box-header with-border">
    <h3 class="box-title">New vehicle</h3>
  </div>
  <div class="box-body">
  </div>
  <div class="overlay">
  </div>
</div>

</div>
</template>

<script>
import 'array-remove-if'
import * as types from '../types.js'

import Aggreg from './aggreg.vue'

const Aggregation = function (esidList, alias) {
  this.reason = null
  this.systemid = -1
  this.esidList = esidList
  this.alias = alias
}

const LightAggreg = function (a) {
  this.alias = a.alias
  this.esidList = a.esidList.map(e => e.esid)
}

export default {
  components: {
    'driconx-aggreg': Aggreg
  },
  props: ['connections'],
  data: function () {
    return {
      'aggregations': [],
      'showNewDrop': false,
      'pruneTimeout': null,
      'aggregateById': true
    }
  },
  watch: {
    'connections': function () {
      this.recomputeAggregations()
    },
    'aggregateById': function () {
      this.recomputeAggregations()
    },
    aggregations: function (aggregations) {
      this.aggregationsChanged(aggregations)
    }
  },
  methods: {
    aliasChanged (aggreg, alias) {
      this.$store.commit(types.CHANGE_AGGREGATION_ALIAS, {
        oldAlias: aggreg.alias,
        newAlias: alias
      })
      aggreg.alias = alias
    },
    aggregationsChanged (aggregations) {
      this.$store.commit(types.CHANGE_AGGREGATIONS, aggregations.map(a => new LightAggreg(a)))
    },
    emptyAggreg (k, aggregation) {
      this.$store.commit(types.DELETE_AGGREGATION, aggregation.alias)
      this.aggregations.splice(k, 1)
    },
    recomputeAggregations: function () {
      var connections = this.connections
      // for each system, check if system is already in aggregation
      for (var i = 0; i < connections.length; i++) {
        var connection = connections[i]
        for (var j = 0; j < connection.systems.length; j++) {
          var system = connection.systems[j]
          var systemAggreg = this.systemAggregation(system, this.aggregateById)
          if (systemAggreg === null) {
            this.aggregations.push(new Aggregation([{ esid: system, connection: connection }], system))
          } else if (systemAggreg.esidList.findIndex(e => e.esid === system) === -1) {
            // remove from all aggregs
            this.aggregations.map(a => a.esidList).forEach(l => l.removeIf(e => e.esid === system))
            // add to aggreg
            systemAggreg.esidList.push({ esid: system, connection: connection })
          }

          // update systems' connections ref
          var candidates = Array.prototype.concat.apply([], this.aggregations.map(a => a.esidList)).filter(s => s.esid === system)
          if (candidates.length > 0) {
            candidates.forEach(c => (c.connection = connection))
          }
        }
      }

      // remove orphan systems from aggregations with a slight timeout because we want to give the uav a chance to respond
      window.clearTimeout(this.pruntTimeout)
      var self = this
      this.pruntTimeout = window.setTimeout(function () {
        self.aggregations.map(a => a.esidList)
        .forEach(l => l.removeIf(e =>
          Array.prototype.concat.apply([], self.connections.map(c => c.systems)).filter(s => s === e.esid).length === 0
        ))
      }, 1200)
    },
    drop: function (targetAggreg, event) {
      var system = JSON.parse(event.dataTransfer.getData('application/json')).esid
      var aggreg = this.systemAggregation(system)

      if (aggreg === null) {
        console.error('Unknown system')
        return
      }

      var index = aggreg.esidList.map(x => x.esid).indexOf(system)
      var detached = aggreg.esidList.splice(index, 1)

      var connection = this.systemConnection(system)

      if (connection === null) {
        console.error('Unknown system connection')
        return
      }
      detached.connection = connection
      detached.esid = system

      targetAggreg.esidList.push(detached)
    },
    deaggregate: function (aggreg) {
      const esidList = aggreg.esidList.slice()
      aggreg.esidList.splice(0, aggreg.esidList.length)
      // We are now waiting for Vue to update the DOM and fire events
      this.$nextTick(function () {
        for (var i = 0; i < esidList.length; i++) {
          var esid = esidList[i]
          this.aggregations.push(new Aggregation([esid], esid.esid))
        }
      })
    },
    dropOnNew: function (event) {
      var system = JSON.parse(event.dataTransfer.getData('application/json')).esid
      var aggreg = this.systemAggregation(system)
      if (aggreg === null) {
        console.error('Unknown system')
        return
      }

      var index = aggreg.esidList.map(x => x.esid).indexOf(system)
      var detached = aggreg.esidList.splice(index, 1)
      this.aggregations.push(new Aggregation(detached, system))
    },
    systemConnection: function (system) {
      // return connection for system
      for (var i = 0; i < this.connections.length; i++) {
        var connection = this.connections[i]
        if (connection.systems.indexOf(system) !== -1) {
          return connection
        }
      }
      return null
    },
    systemAggregation: function (system, aggregateById = false) {
      function isEqualSystem (aggregateById, a, b) {
        if (aggregateById) {
          return a.substring(a.indexOf('-')) === b.substring(b.indexOf('-'))
        } else {
          return a === b
        }
      }

      // return aggregation for system
      for (var k = 0; k < this.aggregations.length; k++) {
        var aggregation = this.aggregations[k]
        if (aggregation.esidList.findIndex(e => isEqualSystem(aggregateById, e.esid, system)) !== -1) {
          return this.aggregations[k]
        }
      }
      return null
    }
  }
}

</script>
