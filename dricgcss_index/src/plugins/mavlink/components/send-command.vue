<template>
  <div class="box box-primary">
    <div class="box-header">
      <h4>
        Send Command
        <button role="button" class="btn btn-sm btn-default" v-on:click="updateAvailableCommands">
          <i class="fa fa-refresh"></i>
        </button>
        <small>
          <span :class="'text-muted ' + (availableCommandsList.length > 0 ? 'bg-success':'bg-danger')">{{availableCommandsList.length}} command{{availableCommandsList.length>0?'s':''}}</span>
        </small>
      </h4>
    </div>
    <div class="box-body">
      <form>
        <my-select2 :options="availableCommandsList" v-model="selected">
          <option disabled value="0">Select one</option>
        </my-select2>

        <div class="form-group" v-for="paramLabel, key in selectedCommandParams">
          <label :for="'paramid'+key">{{paramLabel}}</label>
          <input type="text" class="form-control" :id="'paramid'+key" :placeholder="'PARAM' + key" v-model="param[key]">
        </div>
        <button role="submit" class="btn btn-success" v-on:click.prevent="send">Send</button>
        <span :class="'label label-' + ['success', 'warning', 'danger', 'danger', 'danger'][status]" v-if="status > -1">{{['ACCEPTED', 'TEMPORARILY_REJECTED', 'DENIED', 'UNSUPPORTED', 'FAILED'][status]}}</span>
      </form>
    </div>
  </div>
</template>
<script>
import { watchEsidChange } from './common.js'
import API from '../api'
import select2 from './select2'

const api = new API()

export default {
  components: {
    'my-select2': select2
  },
  data () {
    return {
      commands: [],
      selected: 0,
      param: {
        '1': null,
        '2': null,
        '3': null,
        '4': null,
        '5': null,
        '6': null,
        '7': null
      },
      status: -1
    }
  },
  computed: {
    selectedCommand () {
      const found = this.availableCommandsList.find(c => c.id === parseInt(this.selected[0]))
      if (typeof found !== 'undefined') {
        return found.text
      } else {
        return null
      }
    },
    availableCommandsList () {
      return this.commands.map((c, i) => { return {id: parseInt(i + 1), text: c.name} })
    },
    selectedCommandParams () {
      const filtered = this.commands.filter(c => c.name === this.selectedCommand)[0]
      if (typeof filtered === 'undefined') {
        return {}
      }
      return filtered.param
    }
  },
  watch: {
    selectedCommand () {
      this.$nextTick(function () {
        for (let i in this.param) {
          this.param[i] = null
        }
        this.status = -1
      })
    }
  },
  methods: {
    updateAvailableCommands () {
      const esids = this.$store.getters['driconx/ACTIVE_ESIDS']
      api.getAvailableCommands(esids, c => this.setAvailableCommands(c))
    },
    setAvailableCommands (json) {
      this.commands = json
    },
    send () {
      this.status = -1
      for (var esid of this.$store.getters['driconx/ACTIVE_ESIDS']) {
        const commandId = this.commands.find(c => c.name === this.selectedCommand).id
        api.sendCommand(esid, commandId, Object.values(this.param), status => (this.status = status))
      }
    }
  },
  created () { watchEsidChange.call(this, this.updateAvailableCommands) }
}
</script>
<style>
</style>
