import Map from './mavwp.vue'
import Store from './store'

export const routes = [{
  text: 'Map',
  icon: 'fa fa-location-arrow',
  component: Map,
  name: 'mavmap',
  path: '/map'
}]

export const store = {
  name: 'map',
  module: Store
}
