<template>
  <div class="navbar-custom-menu">
    <ul class="nav navbar-nav">
      <!-- Messages: style can be found in dropdown.less-->
      <li>
        <a href="#" @click.prevent="click" @mousedown="mousedown" @mouseup="mouseup">
          <i class="fa fa-send"></i>
          <span class="label label-danger" v-if="down && !armed">HOLD {{time}}s</span>
          <span class="label label-success" v-if="armed">Armed</span>
          <span class="label label-warning" v-if="!armed && !down">Disarmed</span>
        </a>
      </li>
    </ul>
  </div>
</template>
<script>
import API from './api'

const api = new API()

export default {
  data () {
    return {
      down: false,
      time: 1,
      armed: false
    }
  },
  watch: {
    vehicleEsid () {
      api.subscribe(this.vehicleEsid, this.update)
    }
  },
  computed: {
    vehicleEsid () {
      return this.$store.getters['driconx/ACTIVE_ESIDS'].find(() => true)
    }
  },
  methods: {
    arm () {
      api.arm(this.vehicleEsid)
    },
    disarm () {
      api.disarm(this.vehicleEsid)
    },
    click () {},
    mousedown () {
      if (this.armed) {
        this.disarm()
        return
      }
      this.down = true
      window.clearInterval(this.interval)
      this.time = 1
      this.interval = window.setInterval(function () {
        this.time--
        if (this.time < 0) { this.arm() }
        if (!this.down || this.time < 0) {
          this.time = null
          window.clearInterval(this.interval)
        }
      }.bind(this), 1000)
    },
    mouseup () {
      this.down = false
      this.time = null
    },
    update (esid, state) {
      if (esid === this.vehicleEsid) {
        this.armed = state
      }
    }
  },
  mounted () {
    api.subscribe(this.vehicleEsid, this.update)
  }
}
</script>
<style>
</style>
