<template>
  <div class="wrapper">
    <header class="main-header">
      <dric-navbar></dric-navbar>
    </header>
    <dric-sidebar></dric-sidebar>
    <div class="content-wrapper" style="position:relative">
      <keep-alive>
        <router-view></router-view>
      <keep-alive>
    </div>
  </div>
</template>

<script>
let components = {}
let regexp = new RegExp('.*/(.*)\\.vue')
function requireAll (x) { x.keys().forEach(r => (components[regexp.exec(r)[1]] = x(r))) }
requireAll(require.context('./plugins/', true, /\.vue$/))

import Sidebar from 'components/sidebar'
import Navbar from 'components/navbar'

components['dric-sidebar'] = Sidebar
components['dric-navbar'] = Navbar

export default {
  name: 'app',
  components: components
}

</script>

<style>
</style>
