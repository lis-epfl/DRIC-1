import Driconx from './driconx.vue'
import 'array-remove-if'
import Store from './store.js'

export const store = {
  name: 'driconx',
  module: Store
}

export const routes = [{
  text: 'Connections',
  icon: 'fa fa-wifi',
  component: Driconx,
  name: 'connections',
  path: '/connections'
}]

export const navbar = {
  'driconx-choose-aggreg': 'navbar/nav-choose-aggreg.vue'
}

export const hooks = {
  postInit: function () {
    console.log('post')
    this.$router.push({path: '/connections'})
  }
}
