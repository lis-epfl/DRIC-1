import Vuex from 'vuex'
import Vue from 'vue'

Vue.use(Vuex)

let modules = {}
function requireAll (x) { x.keys().map(r => x(r).store).filter(r => typeof r !== 'undefined').forEach(r => (modules[r.name] = r.module)) }
requireAll(require.context('../plugins/', true, /\/index.js$/))

const store = new Vuex.Store({
  state: {
    routes: [],
    drichost: 'localhost:80'
  },
  mutations: {
    addRoute (state, route) {
      state.routes.push(route)
    }
  },
  modules,
  strict: process.env.NODE_ENV !== 'production'
})

export default store
