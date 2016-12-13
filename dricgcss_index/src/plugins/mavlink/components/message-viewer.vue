<template>
  <div class="box box-default">
    <div class="box-header">
      <div class="dropdown">
        <span>Data acquisition&nbsp;</span>
        <div class="acquisition">
          <div class="button">
            <button title="Start now" :class="'btn btn-default btn-sm ' + (acquiring?'active':'')" v-on:click="acquiring = !acquiring; startAcquisition()">
              <i class="fa fa-circle"></i>
            </button>
          </div>
          <div class="progress-wrapper" v-if="acquiring">
            <div class="progress progress active acquisition-progress">
              <div class="progress-bar progress-bar-default progress-bar-striped" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%">
              </div>
            </div>
          </div>
          <div class="button" v-if="acquiring">
            <a title="Download" class="btn btn-default btn-sm" :href="fullAcquiringHref" target="_blank" v-bind:download="type + '.txt'">
              <i class="fa fa-download"></i>
            </a>
          </div>
          <div class="button">
            <a title="Download all" class="btn btn-primary btn-sm" :href="fullAllTimeHref" v-bind:download="type + '.txt'">
              <i class="fa fa-download"></i>
            </a>
          </div>
        </div>
      </div>
    </div>
    <div class="box-body">
      {{type}}${{esid}}
      <table class="table table-striped">
        <tbody>
          <tr v-for="(value, key) in $store.getters[types.SHOWN_MESSAGE_CONTENT]">
            <td>{{key}}</td>
            <td>{{convertMavlink(type, key, value)}} {{type in units ? units[type][key]:''}}</td>
            <td style="text-align:right">
              <div class="btn-group">
                <button class="btn btn-default dropdown-toggle btn-sm" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" v-if="type in units && key in units[type]">
                  <i class="fa fa-exchange"></i>
                </button>
                <a v-if="acquiring" class="btn btn-default btn-sm" target="_blank" v-bind:href="acquiringHref(key)" v-bind:download="type + '.' + key + '.txt'">
                  <i class="fa fa-download"></i>
                </a>
                <a class="btn btn-primary btn-sm" target="_blank" v-bind:href="allTimeHref(key)" v-bind:download="type + '.' + key + '.txt'">
                  <i class="fa fa-download"></i>
                </a>
                <ul v-if="type in units && key in units[type] && getConvertableUnitsFor(units[type][key]) !== null" class="dropdown-menu">
                  <li v-for="unit in getConvertableUnitsFor(units[type][key])">
                    <a v-on:click="units[type][key]=unit">{{unit}}</a>
                  </li>
                </ul>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
</template>
<script>
import * as types from '../types.js'
import { MessagesViewerConfig } from '../config'
import API from '../api'
import $ from 'jquery'
import { convert } from '../conversion.js'

const Conversion = window.Conversion
const api = new API(MessagesViewerConfig)

const UNITS = {}
const units = {}
api.getUnits(function (distunits) {
  $.extend(true, UNITS, distunits)
  $.extend(true, units, distunits)
})

export default {
  data () {
    return {
      acquisition: 'boot',
      message: {},
      inspectedMessageType: null,
      acquiring: false,
      types,
      units,
      from: 0
    }
  },
  methods: {
    allTimeHref (key) {
      return api.allHref(this.type, this.$store.getters['driconx/ACTIVE_ESIDS'], [key])
    },
    acquiringHref (key) {
      return api.allHref(this.type, this.$store.getters['driconx/ACTIVE_ESIDS'], [key], this.from)
    },
    startAcquisition () {
      api.getServerTime((r) => (this.startTime = r))
    },
    getQuantityFor (unit) {
      for (let q in Conversion.quantities) {
        if (Conversion.quantities[q].indexOf(unit) >= 0) {
          return q
        }
      }
      return null
    },
    getConvertableUnitsFor (unit) {
      const quantity = this.getQuantityFor(unit)
      if (quantity === null) {
        return null
      } else {
        // override to display only the most important units
        switch (quantity) {
          case 'length': return ['nm', 'um', 'mm', 'cm', 'm', 'km']
          case 'temperature': return ['°C', '°F']
        }
        return Conversion.quantities[quantity]
      }
    },
    convertMavlink (type, key, value) {
      if (type in UNITS && key in UNITS[type] && type in this.units && key in this.units[type]) {
        var from = UNITS[type][key]
        var to = this.units[type][key]
        return convert(from, to, value)
      } else {
        return value
      }
    }
  },
  watch: {
    acquiring (acquiring) {
      api.getServerTime((t) => (this.from = t))
    }
  },
  computed: {
    type () { return this.$store.getters[types.SHOWN_MESSAGE_TYPE] },
    esid () { return this.$store.getters[types.SHOWN_MESSAGE_ESID] },
    fullAllTimeHref () {
      if (typeof this.type === 'undefined') {
        return '#'
      }
      return api.allHref(this.type, this.$store.getters['driconx/ACTIVE_ESIDS'], Object.keys(this.$store.getters[types.SHOWN_MESSAGE_CONTENT]))
    },
    fullAcquiringHref () {
      if (typeof this.type === 'undefined') {
        return '#'
      }
      return api.allHref(this.type, this.$store.getters['driconx/ACTIVE_ESIDS'], Object.keys(this.$store.getters[types.SHOWN_MESSAGE_CONTENT]), this.from)
    }
  },
  created () {
    this.$store.watch(() => this.$store.getters[types.GET_INSPECTED_MESSAGE_TYPE], t => (this.inspectedMessageType = t))
  }
}
</script>
<style lang="less">
.acquisition {
  position: relative;
  .button {
    width: 15%;
    display: inline;
    :first-child {
      text-align: right;
    }
    :last-child {
      text-align: left;
    }
  }
  .progress-wrapper {
    display: inline-block;
    width: 55%;
    .progress {
      margin-bottom: -6px;
    }
  }
}
</style>
