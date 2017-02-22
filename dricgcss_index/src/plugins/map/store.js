import * as types from './types.js'
// import Config from './config'

export default {
  state: {
    maplayer: 'Stamen',
    overlay: null
  },
  mutations: {
    [types.MAP_LAYER] (state, maplayer) {
      state.maplayer = maplayer
    },
    [types.MAP_OVERLAY] (state, overlay) {
      state.overlay = overlay
    }
  },
  getters: {
    [types.GET_MAP_LAYER] (state) {
      return state.maplayer
    },
    [types.GET_MAP_OVERLAY] (state) {
      return state.overlay
    }
  },
  actions: {}
}
