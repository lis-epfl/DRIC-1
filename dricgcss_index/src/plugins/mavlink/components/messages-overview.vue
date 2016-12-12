<template>
  <div class="box box-primary">
    <div class="box-body">
      <input type="text" class="form-control" v-model="searchquery" placeholder="Search..." />
      <table id="mavlink-messages-overview" class="table table-striped">
        <thead>
          <tr>
            <th>Type</th>
            <th>Count</th>
            <th>Frequency (Hz)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="message in messages" v-if="message.type.toUpperCase().indexOf(searchquery.toUpperCase()) > -1">
            <td>
              <a role="button" v-on:click="openMavlinkMsg(message.type)" v-bind:data-message-type="message.type">
                {{message.type}}
              </a>
            </td>
            <td>{{message.count}}</td>
            <td>
              <tt v-for="frequency, esid in message.frequency" :title="esid">
                {{sprintf('%-4d', frequency)}}
              </tt>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script>
import { watchEsidChange } from './common.js'
import WebSocketDatasource from 'websocket-datasource'
import Url from 'url'
import { MessagesOverviewConfig } from '../config'
import 'dataview-getstring'
import { sprintf } from 'sprintf-js'
import * as types from '../types.js'

const urlTemplate = Url.format({
  protocol: MessagesOverviewConfig.protocol,
  port: MessagesOverviewConfig.port,
  hostname: MessagesOverviewConfig.hostname,
  pathname: MessagesOverviewConfig.pathname,
  search: MessagesOverviewConfig.search('mavlink/messages_stats$__REPLACEME__')
})

const FrequencyHelper = function () {
  const frequencies = {}
  const UPDATE_PERIOD = 5 // update every N seconds

  this.update = function (esid, type, count, time) {
    if (!(type in frequencies)) {
      frequencies[type] = { }
    }
    const fst = frequencies[type]
    if (!(esid in fst)) {
      fst[esid] = { count, time, frequency: 0 }
      return
    }
    const fste = fst[esid]

    if (time - fste.time > UPDATE_PERIOD) {
      fste.frequency = (count - fste.count) / (time - fste.time)

      fste.count = count
      fste.time = time
    }
  }

  this.getFrequencies = function (type) {
    const fst = frequencies[type]
    const out = {}
    for (let esid in fst) {
      out[esid] = Math.round(fst[esid].frequency)
    }
    return out
  }
}

export default {
  data () {
    return {
      searchquery: '',
      datasources: [],
      inputs: {}, // [esid] = {time, stats = {type: count}}
      last: {} // [esid][type] = {count, time}
    }
  },
  computed: {
    messages () {
      const counts = {}
      const messages = []
      for (let esid in this.inputs) {
        if (!(esid in this.last)) {
          this.last[esid] = { stats: {} }
        }
        for (let type in this.inputs[esid].stats) {
          const myinputs = this.inputs[esid]
          if (!(type in counts)) {
            counts[type] = 0
          }
          counts[type] += myinputs.stats[type]
          this.frequencyHelper.update(esid, type, myinputs.stats[type], myinputs.time)
        }
      }
      for (let type in counts) {
        messages.push({
          type,
          frequency: this.frequencyHelper.getFrequencies(type),
          count: counts[type]
        })
      }
      return messages
    }
  },
  methods: {
    sprintf,
    openMavlinkMsg (messageType) {
      this.$store.dispatch(types.SHOW_MESSAGE_TYPE, messageType)
    },
    onStats (esid, m) {
      let view = new DataView(m.data)
      let time = view.getFloat64(0)
      let jsonText = view.getString(8)
      let stats = JSON.parse(jsonText)

      this.$set(this.inputs, esid, { stats, time })
    },
    openDatasource (esids) {
      this.datasources.forEach(d => d.close())

      this.inputs = {}
      this.frequencyHelper = new FrequencyHelper()

      for (let i = 0; i < esids.length; i++) {
        const esid = esids[i]
        const datasource = new WebSocketDatasource(urlTemplate.replace('__REPLACEME__', esid))
        this.datasources.push(datasource)
        datasource.onmessage = (m) => this.onStats(esid, m)
      }
    }
  },
  created () { watchEsidChange.call(this, this.openDatasource) }
}
</script>
