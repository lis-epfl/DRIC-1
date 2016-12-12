import * as types from './types.js'

export default {
  state: {
    aggregations: [],
    activeAggregation: null
  },
  mutations: {
    [types.CHANGE_AGGREGATIONS] (state, aggregations) {
      state.aggregations.splice(0, state.aggregations.length)
      aggregations.forEach(a => state.aggregations.push(a))
    },
    [types.CHANGE_AGGREGATION_ALIAS] (state, change) {
      state.aggregations
        .filter(x => x.alias === change.oldAlias)
        .forEach(x => (x.alias = change.newAlias))
    },
    [types.DELETE_AGGREGATION] (state, alias) {
      state.aggregations.map(x => x.alias)
      state.aggregations.removeIf(x => x.alias === alias)
    },
    [types.ACTIVE_AGGREGATION] (state, aggregation) {
      state.activeAggregation = aggregation
    }
  },
  getters: {
    [types.ACTIVE_ESIDS] (state) {
      if (state.activeAggregation !== null) {
        return state.activeAggregation.esidList
      } else {
        return []
      }
    }
  }
}
