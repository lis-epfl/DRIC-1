import Mavlink from './mavlink.vue'
import Store from './store.js'

export const store = {
  name: 'mavlink',
  module: Store
}

export const routes = [{
  text: 'Mavlink',
  icon: 'fa fa-link',
  component: Mavlink,
  name: 'mavlink',
  path: '/mavlink'
}]
