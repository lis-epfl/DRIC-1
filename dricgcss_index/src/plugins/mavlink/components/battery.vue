<template>
  <!-- Show settings -->
  <div class="info-box" v-if="showSettings">
    <span class="info-box-icon bg-gray">
      <i class="fa fa-battery-half"></i>
    </span>
    <div class="info-box-content">
      <span class="info-box-text">Battery Setting
        <a href="#" class="pull-right text-success" v-on:click.prevent="showSettings=false">
          <i class="fa fa-repeat"></i>
        </a>
      </span>
      <span class="progress-description">
        Source message type:
        <div class="form-inline">
            <select class="form-control" v-model="source">
              <option :value="source_name" v-for="source_name in sources">
              {{source_name}}
              </option>
            </select>
        </div>
      </span>
    </div>
  </div>
  <!-- Show infos -->
  <div class="info-box bg-yellow" v-else>
    <span class="info-box-icon">
      <i class="fa fa-battery-half"></i>
    </span>
    <div class="info-box-content">
      <span class="info-box-text">Battery
        <a href="#" class="pull-right" v-on:click.prevent="showSettings=true"><i class="fa fa-cog"></i></a>
      </span>
      <span class="info-box-number">{{battery.tension}}mV </span>
      <span class="progress-description">{{battery.remaining}}% remaining ({{battery.current}}mAh)</span><div class="progress">
        <div class="progress-bar" v-bind:style="{width: battery.remaining+'%'}"></div>
      </div>
    </div>
  </div>
</template>
<script>
import { BatteryConfig } from '../config'
import Mavlink from '../api/ws/mavws'
import { watchEsidChange } from './common.js'

export default {
  data () {
    return {
      mavlinkSubscibers: [],
      showSettings: false,
      source: 'SYS_STATUS',
      battery: {
        voltage: 0,
        current: 0,
        remaining: 0
      },
      esids: null
    }
  },
  computed: {
    sources () {
      return Object.keys(BatteryConfig.mapping)
    },
    activeEsids () {
      if (typeof this.$store.driconx !== 'undefined') {
        console.log(this.$store.driconx.activeEsids)
        return this.$store.driconx.activeEsids
      } else {
        return []
      }
    }
  },
  watch: {
    source () { this.subscribe(this.$store.getters['driconx/ACTIVE_ESIDS']) }
  },
  methods: {
    onMavlink (time, value, info) {
      let mapping = BatteryConfig.mapping[info.messageType]
      for (let k in mapping) {
        if (mapping[k] === info.fieldName) {
          this.battery[k] = value
        }
      }
    },
    subscribe (esids) {
      // unsubscribe from all mavlink listeners
      this.mavlinkSubscibers.splice(0, this.mavlinkSubscibers.length).forEach(x => x())

      // and resubscribe with new esids
      const self = this
      for (let i = 0; i < esids.length; i++) {
        const esid = esids[i]
        for (let field in this.battery) {
          const subscriber = Mavlink.subscribe(this.source, BatteryConfig.mapping[this.source][field], esid,
            function (time, value) {
              self.onMavlink(time, value, this)
            })
          this.mavlinkSubscibers.push(subscriber)
        }
      }
    }
  },
  created () { watchEsidChange.call(this, this.subscribe) }
}
</script>

<style lang="less">
@import '../../../../node_modules/bootstrap-less/bootstrap/variables.less';

.info-box.bg-yellow .info-box-text a {
  color: white;
  :hover {
    color: @gray-lighter;
  }
}
</style>
