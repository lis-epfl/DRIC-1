<template>
  <section class="content body page">
    <section class="content-header">
      <h1>
        Parameters
      </h1>
      <button role="button" class="btn btn-primary" @click="refreshParameterList" :disabled="esids.length == 0 || listing">
        <i class="fa fa-refresh"></i>
        Refresh list
      </button>
      <div :class="{progress: true, active: receivedParamCount < totalParamCount}">
        <div :class="{'progress-bar': true, 'progress-bar-green': paramListStatus === 'success', 'progress-bar-yellow': paramListStatus === 'timeout', 'progress-bar-striped': receivedParamCount < totalParamCount}"
        role="progressbar" :aria-valuenow="receivedParamCount" :aria-valuemin="0" :aria-valuemax="totalParamCount" :style="{width: totalParamCount == 0?0:(receivedParamCount/totalParamCount)*100+'%'}">
          <span class="sr-only" v-if="receivedParamCount < totalParamCount">{{receivedParamCount}}/{{totalParamCount}}</span>
          <span v-if="receivedParamCount == totalParamCount && totalParamCount > 0 && paramListStatus==='status'">{{receivedParamCount}}/{{totalParamCount}}</span>
          <span v-if="paramListStatus==='timeout'">Timeout</span>
        </div>
      </div>
      <div class="box box-primary">
        <div class="box-body">
          <input type="text" placeholder="Search by id or index..." class="form-control" v-model="search">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>
                  Index
                </th>
                <th>
                  Id
                </th>
                <th>
                  Value
                  <button @click="locked=!locked" class="btn btn-default btn-sm">
                    <i :class="{fa: true, 'fa-fw': true, 'fa-lock': locked, 'fa-unlock': !locked}"></i>
                  </button>
                </th>
                <th>
                  Type
                </th>
                <th>
                  System
                </th>
                <th>
                  Component
                </th>
                <th>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pv in filteredParamValues">
                <td>
                  {{pv.param_index}}
                </td>
                <td>
                  {{pv.param_id}}
                </td>
                <td class="form-inline">
                  <input type="text" v-model="pv.param_value" :disabled="locked" class="form-control"/>
                </td>
                <td>
                  {{humanReadableType(pv.param_type)}}
                </td>
                <td>
                  {{pv.srcSystem}}
                </td>
                <td>
                  {{pv.srcComponent}}
                </td>
                <td>
                  <div class="btn-group">
                    <button role="button" class="btn btn-default" title="read" @click="requestRead(pv)">
                      <i class="fa fa-download"></i>
                    </button>
                    <button role="button" class="btn btn-default" title="write" @click="paramSet(pv)" :disabled="locked">
                      <i class="fa fa-upload"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </section>
</template>
<script>
import API from './api'

const api = new API()

export default {
  data () {
    return {
      totalParamCount: 0,
      receivedParamCount: 0,
      paramvalues: [],
      search: '',
      paramListStatus: 'success',
      listing: false,
      locked: true
    }
  },
  computed: {
    esids () {
      const esids = this.$store.getters['driconx/ACTIVE_ESIDS']
      if (typeof esids === 'undefined') {
        return []
      }
      return esids
    },
    filteredParamValues () {
      if (this.search.length === 0) {
        return this.paramvalues
      }
      return this.paramvalues.filter(pv => pv.param_id.toUpperCase().indexOf(this.search.toUpperCase()) >= 0 || pv.param_index.toString() === this.search)
    }
  },
  methods: {
    refreshParameterList () {
      if (this.esids.length === 0) {
        return
      }
      this.receivedParamCount = 0
      this.totalParamCount = 0
      this.paramListStatus = 'success'
      this.paramvalues = []
      const esid = this.esids.find(() => true)
      const parap = api.paramRequestList(esid)
      this.listing = true
      parap.onparamvalue = (pv) => {
        this.totalParamCount = pv.param_count
        this.receivedParamCount++
        this.paramvalues.push(pv)
        this.paramvalues.sort((a, b) => a.param_index - b.param_index)
      }
      parap.onclose = () => (this.listing = false)
      parap.ontimeout = () => (this.paramListStatus = 'timeout')
    },
    requestRead (param) {
      const esid = this.esids.find(() => true)
      console.log(param)
      const parap = api.paramRequestRead(esid, param.param_index)
      parap.onparamvalue = pv => Object.assign(param, pv)
    },
    paramSet (param) {
      // Allow user to create new parameters ?
      const esid = this.esids.find(() => true)
      const parap = api.paramSet(esid, param.param_id, param.param_value, param.param_type, param.srcComponent)
      parap.onparamvalue = pv => Object.assign(param, pv)
    },
    humanReadableType (type) {
      // see MAV_PARAM_TYPE enum @ https://pixhawk.ethz.ch/mavlink
      return {
        '1': 'MAV_PARAM_TYPE_UINT8',
        '2': 'MAV_PARAM_TYPE_INT8',
        '3': 'MAV_PARAM_TYPE_UINT16',
        '4': 'MAV_PARAM_TYPE_INT16',
        '5': 'MAV_PARAM_TYPE_UINT32',
        '6': 'MAV_PARAM_TYPE_INT32',
        '7': 'MAV_PARAM_TYPE_UINT64',
        '8': 'MAV_PARAM_TYPE_INT64',
        '9': 'MAV_PARAM_TYPE_REAL32'
      }[type]
    }
  }
}
</script>
<style>
.progress {
  max-width: 300px;
}
.progress-bar {
  transition: 0;
}
</style>
