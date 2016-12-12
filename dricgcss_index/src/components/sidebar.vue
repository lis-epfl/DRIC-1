<template>
  <div class="main-sidebar">
    <div class="sidebar">
      <!-- Sidebar Menu -->
      <ul class="sidebar-menu">
          <router-link :to="item.path"
                    tag="li"
                    active-class="active"
                    v-for="item in $store.state.routes">
            <a>
              <i :class="item.icon"></i>
              <span>{{item.text}}</span>
            </a>
          </router-link>
      </ul><!-- /.sidebar-menu -->
    </div><!-- /.sidebar -->
  </div><!-- /.main-sidebar -->
</template>

<script>
let items = []
function requireAll (x) { x.keys().forEach(r => items.push(x(r).sidebar)) }
requireAll(require.context('../plugins/', true, /\/index.js$/))

export default {
  name: 'dric-sidebar'
}

</script>

<style>
</style>
