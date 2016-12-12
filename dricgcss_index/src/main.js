import Vue from 'vue'

// Router
import VueRouter from 'vue-router'
Vue.use(VueRouter)

// Store
import store from './store'

// App component
import App from './App'

// Stylesheets
import './assets/style.less'

// Javascript libararies
import 'expose?$!expose?jQuery!jquery'
import 'jquery-ui'
import 'bootstrap'
import 'bootstrap-slider'
import 'datatables.net'
import '../node_modules/admin-lte/dist/js/app.min.js'

import flatten from 'array-flatten'

// Utility functions
const deepcopy = function (x) {
  return JSON.parse(JSON.stringify(x))
}

/* const defined = function (x) {
  return typeof x !== 'undefined'
} */

// Add routes
let routes = []
function requireAll (x) { x.keys().forEach(r => routes.push(x(r).routes)) }
requireAll(require.context('./plugins/', true, /\.\/[^/]+\/index.js$/))

routes = flatten(routes)  // flatten routes array
  .filter(r => r)         // filter undefined/not object value

// add routes to store
routes
  .forEach(r => store.commit('addRoute', deepcopy(r)))

// initialize router
const router = new VueRouter({
  routes
})

/* eslint-disable no-new */
const vue = new Vue({
  el: '#app',
  store,
  router,
  template: '<App/>',
  components: { App }
})

// post init hooks
function postInitHooks (x) {
  x.keys().map(r => x(r).hooks)
    .filter(f => typeof f !== 'undefined')
    .map(h => h.postInit)
    .filter(f => typeof f !== 'undefined')
    .forEach(h => h.call(vue))
}
postInitHooks(require.context('./plugins/', true, /\.\/[^/]+\/index.js$/))
