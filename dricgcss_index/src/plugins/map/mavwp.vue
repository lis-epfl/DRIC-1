<template>
  <section class="content body page" id="page-map">
    <div class="row">
      <div id="dric-map">
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <div class="col-md-7">
          <mav-map :esid="vehicleEsid" :waypoints="waypoints" :selectedWaypoint="selectedWaypoint" @mapcenter="mapcenter=$event"></mav-map>
        </div>
        <!--<div class="form-group col-md-3">
          <label>Choose a map tile</label>
          <select class="form-control map-select-tiles"></select>
        </div>-->
        <!--<div class="form-group col-md-3">
          <label>Map tools</label>
          <div class="btn-toolbar" role="toolbar">
            <div class="btn-group" data-toggle="buttons">
              <label class="btn btn-default"><input type="radio" name="options" id="map-toolbar-cursor" checked="checked"><i class="fa fa-mouse-pointer"></i></label>
              <label class="btn btn-default"><input type="radio" name="options" id="map-toolbar-waypoint"><i class="fa fa-map-marker"></i></label>
            </div>
          </div>
        </div>-->
        <div class="col-md-3">
          <div class="box">
            <div class="box-body">
              <div class="form-group">
                <label>{{count}} waypoints on system</label>
                <select size="5" class="form-control" id="map-select-waypoint" v-model="selectedWaypoint">
                  <option v-for="waypoint, index in waypoints" :value="waypoint" :style="{'font-weight': waypoint.current ? 'bold':null}">
                    [{{index}}] {{commandAlias[waypoint.command]}}
                  </option>
                </select>
                <div class="btn-toolbar" role="toolbar">
                  <div class="btn-group pull-left">
                    <button role="button" class="btn btn-success" title="Send to vehicle" @click="writeToVehicle">
                      <i class="fa fa-chevron-left"></i>
                      send all
                    </button>
                    <button role="button" class="btn btn-primary" title="Receive from vehicle" @click="readFromVehicle">
                      recv all
                      <i class="fa fa-chevron-right"></i>
                    </button>
                  </div>
                  <div class="btn-group" data-toggle="buttons">
                    <button class="btn btn-default" @click="addNewWP" title="new">
                      <i class="fa fa-plus"></i>
                    </button>
                    <button class="btn btn-default" @click="deleteWaypoint(selectedWaypoint)">
                      <i class="fa fa-trash"></i>
                    </button>
                    <button class="btn btn-default" @click="updownwp(selectedWaypoint, +1)" :disabled="!(selectedWaypoint && selectedWaypoint.seq + 1 < waypoints.length)">
                      <i class="fa fa-arrow-down"></i>
                    </button>
                    <button class="btn btn-default" @click="updownwp(selectedWaypoint, -1)" :disabled="!(selectedWaypoint && selectedWaypoint.seq - 1 >= 0)">
                      <i class="fa fa-arrow-up"></i>
                    </button>
                  </div>
                  <a title="download" class="map-save-waypoints btn btn-default" :href="fileUrl" download="waypoints.json">
                    <i class="fa fa-download"></i>
                  </a>
                  <label>
                    <a role="button" class="btn btn-default" title="Upload">
                      <i class="fa fa-upload"></i>
                    </a>
                    <input id="map-waypoints-file" style="display:none" type="file" @change="uploaded($event);$el.input='';$el.input=''">
                  </label>
                </div>
              </div>
            </div>
          </div>
          <mav-map-chooser :waypoints="waypoints" :selectedWaypoint="selectedWaypoint" @inWaypoint="selectedWaypoint=$event" @inSelectedWaypoint="selectedWaypoint=$event"></mav-map-chooser>
          <mav-custom-commands :esid="vehicleEsid"></mav-custom-commands>
        </div>
        <div class="col-md-2">
          <div class="box form-horizontal col-md-12">
            <div class="box-body" v-if="selectedWaypoint">
              <div class="form-group" style="text-align:right">
                <!--<button role="button" class="btn btn-default btn-sm pull-left" title="Show help" @click="showHelp=!showHelp">
                  <span class="fa-stack">
                    <i class="fa fa-info fa-stack-1x"></i>
                    <i class="fa fa-ban fa-stack-2x" v-if="!showHelp"></i>
                    <i class="fa fa-circle-o fa-stack-2x" v-if="showHelp"></i>
                  </span>
                </button>-->
                <div class="btn-group">
                  <button role="button" class="btn btn-success" title="Set current" @click="setCurrent(selectedWaypoint)">
                    <i class="fa fa-star"></i> Set current
                  </button>
                </div>
              </div>
              <div class="form-group" :title="commandsById[selectedWaypoint.command].description">
                <label class="col-sm-5">Command:</label>
                <select class="col-sm-7 waypoint-control" v-model="selectedWaypoint.command">
                  <option v-for="command in sortedCommands.filter(o => o.name.startsWith('MAV_CMD_NAV_'))" :value="command.id">
                    {{command.name}}
                  </option>
                </select>
                <p class="help-block col-sm-7" v-if="showHelp">{{commandsById[selectedWaypoint.command].description}}</p>
              </div>
              <div class="form-group" :title="framesById[selectedWaypoint.frame].description">
                <label class="col-sm-5">Frame:</label>
                <select class="col-sm-7 waypoint-control" v-model="selectedWaypoint.frame">
                  <option v-for="frame in sortedFrames" :value="frame.id">
                    {{frame.name}}
                  </option>
                </select>
                <p class="help-block col-sm-7" v-if="showHelp">{{framesById[selectedWaypoint.frame].description}}</p>
              </div>
              <div class="form-group" v-for="param, key in paramInCommandsById[selectedWaypoint.command]" :title="param">
                <label class="col-sm-5">{{['param1','param2','param3','param4','x','y','z'][key-1]}}:</label>
                <input type="text" class="col-sm-7" v-model="selectedWaypoint[['param1','param2','param3','param4','x','y','z'][key-1]]" />
                <p class="help-block col-sm-7 col-sm-offset-5" v-if="showHelp">{{param}}</p>
              </div>
              <div class="form-group" >
                <label class="col-sm-5">Autocontinue:</label>
                <input type="checkbox" v-model="selectedWaypoint.autocontinue" />
                <p class="help-block col-sm-7 col-sm-offset-5" v-if="showHelp">Autocontinue to next waypoint</p>
              </div>
            </div>
            <div class="box-body" v-else>
              <p style="text-align:center">
                Please choose a waypoint to inspect.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
<script>
import MavMapChooser from './MavMapChooser'
import MavMap from './mavmap'
import MavCustomCommands from './mavcommands'
import API from './api'
const api = new API()

export default {
  components: {
    'mav-map-chooser': MavMapChooser,
    'mav-map': MavMap,
    'mav-custom-commands': MavCustomCommands
  },
  data () {
    return {
      count: 0,
      waypoints: [],
      selectedWaypoint: null,
      commands: [],
      showHelp: false,
      frames: [],
      mapcenter: {x: 0, y: 0}
    }
  },
  watch: {
    vehicleEsid () {
      this.count = 0
      this.waypoints = []
      api.getAvailableCommands([this.vehicleEsid], c => (this.commands = c))
      api.getAvailableFrames([this.vehicleEsid], c => (this.frames = c))
    }
  },
  computed: {
    vehicleEsid () {
      return this.$store.getters['driconx/ACTIVE_ESIDS'].find(() => true)
    },
    commandAlias () {
      return this.commands.reduce((o, c) => Object.defineProperty(o, c.id, {value: c.name}), {})
    },
    commandsById () {
      return this.commands.reduce((o, c) => Object.defineProperty(o, c.id, {value: c}), {})
    },
    framesById () {
      return this.frames.reduce((o, c) => Object.defineProperty(o, c.id, {value: c}), {})
    },
    paramInCommandsById () {
      return this.commands.reduce((o, c) => Object.defineProperty(o, c.id, {value: c.param}), {})
    },
    sortedCommands () {
      return this.commands.sort((a, b) => a.name > b.name ? 1 : a.name < b.name ? -1 : 0)
    },
    sortedFrames () {
      return this.frames.sort((a, b) => a.name > b.name ? 1 : a.name < b.name ? -1 : 0)
    },
    fileUrl () {
      return 'data:text/plain;charset=utf-8,' + JSON.stringify(this.waypoints)
    }
  },
  methods: {
    uploaded (e) {
      const file = e.target.files[0]
      console.log(file)
      if (typeof file === 'undefined') { return }
      const reader = new window.FileReader()
      reader.onload = (e) => (this.waypoints = JSON.parse(e.target.result))
      reader.readAsText(file)
    },
    addNewWP () {
      this.waypoints.push({
        'target_system': 5,
        'target_component': 8,
        'seq': this.waypoints.length,
        'frame': 3,  //   MAV_FRAME_GLOBAL_RELATIVE_ALT
        'command': 16,
        'current': 0,
        'autocontinue': 1,
        'param1': 0,
        'param2': 0,
        'param3': 0,
        'param4': 0,
        'x': this.mapcenter.x,
        'y': this.mapcenter.y,
        'z': 25
      })
    },
    deleteWaypoint (waypoint) {
      const where = this.waypoints.indexOf(waypoint)
      if (waypoint === this.selectedWaypoint) {
        this.selectedWaypoint = null
      }
      if (where > -1) {
        this.waypoints.splice(where, 1)
        this.waypoints.forEach((w, i) => (w.seq = i))
      }
    },
    updownwp (waypoint, direction) {
      if (waypoint.seq + direction < this.waypoints.length && waypoint.seq + direction >= 0) {
        for (let wp of this.waypoints) {
          if (wp.seq === waypoint.seq + direction) {
            wp.seq -= direction
            waypoint.seq += direction
            break
          }
        }
        this.waypoints.sort((a, b) => a.seq - b.seq)
      }
    },
    setCurrent (waypoint) {
      api.setCurrent(this.vehicleEsid, waypoint.seq)
    },
    readFromVehicle () {
      this.waypoints.forEach(w => (w.damn = true))
      api.readFromVehicle(this.vehicleEsid)
    },
    writeToVehicle () {
      api.writeToVehicle(this.vehicleEsid, this.waypoints)
    },
    updateMissionCount (count, esid) {
      if (esid === this.vehicleEsid) {
        this.count = count
        if (this.count !== this.waypoints.length) {
          this.waypoints = []
        }
      }
    },
    updateMissionItem (item, esid) {
      if (esid === this.vehicleEsid) {
        // merge existing with new one
        const old = this.waypoints.find(w => w.seq === item.seq)
        if (old) {
          Object.assign(old, item)
        } else {
          this.waypoints.push(item)
        }
        this.waypoints.sort((a, b) => a.seq - b.seq)
      }
    },
    updateMissionCurrent (seq, esid) {
      if (esid === this.vehicleEsid) {
        this.waypoints.forEach(w => (w.current = (w.seq === seq ? 1 : 0)))
      }
    },
    updateMissionAck (type, esid) {
      if (esid === this.vehicleEsid) {
        console.log(type)
      }
    }
  },
  mounted () {
    api.updateMissionCount = this.updateMissionCount
    api.updateMissionItem = this.updateMissionItem
    api.updateMissionCurrent = this.updateMissionCurrent
    api.updateMissionAck = this.updateMissionAck
    api.getAvailableCommands([this.vehicleEsid], c => (this.commands = c))
    api.getAvailableFrames([this.vehicleEsid], c => (this.frames = c))
  }
}
</script>
<style lang="less">
#page-map {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  &>.row:last-child {
    height: 100%;
    &>div:first-child {
      height: 100%;
      &>div:first-child {
        height: 100%;
      }
    }
  }
}
</style>
