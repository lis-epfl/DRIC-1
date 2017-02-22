<template>
  <div class="navbar-custom-menu">
    <ul class="nav navbar-nav ">
      <li class="dropdown messages-menu">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown" aria-expanded="true">
          <i class="fa fa-link"></i>
          &nbsp;
          <span :class="active&&active.alias==='No system connected'?'ohmy':''">{{active?active.alias:'No system connected'}}</span>
        </a>
        <ul class="dropdown-menu">
          <li class="header">You have {{aggregations.length}} UAV{{aggregations.length > 1?'s':''}}</li>
          <li v-for="aggregation in aggregations">
            <a href="#" v-on:click.prevent="active=aggregation"><tt>{{aggregation.alias}}</tt></a>
          </li>
          <li class="footer">
              <router-link to="/connections">Modify connections</router-link>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>
import * as types from '../types.js'

export default {
  data () {
    return {
      active: null
    }
  },
  computed: {
    aggregations () {
      return this.$store.state.driconx.aggregations
    }
  },
  watch: {
    aggregations (aggregations) {
      if (this.active === null) {
        if (aggregations.length >= 1) {
          this.active = aggregations[0]
        }
        return
      }
      if (aggregations.map(a => a.alias).indexOf(this.active.alias) === -1) {
        this.active = null
      }
    },
    active (active) {
      this.$store.commit(types.ACTIVE_AGGREGATION, active)
    }
  }
}

</script>

<style lang="less">
// Easter egg when the user names an aggregation 'No systems connected'
.ohmy {
  animation-name: ohmyan;
  animation-duration: 2s;
  animation-iteration-count: infinite;
}

@keyframes ohmyan {
  0% {color: inherit;}
  10% {color: green;}
  20% {color: pink;}
  30% {color: orange;}
  40% {color: blue;}
  50% {color: fuchsia;}
  60% {color: greenyellow;}
  70% {color: aqua;}
  80% {color: goldenrod;}
  90% {color: beige;}
  100% {color: deeppink;}
}
</style>
