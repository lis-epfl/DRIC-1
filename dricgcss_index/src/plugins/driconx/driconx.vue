<template>
  <section class="content body page">
    <section class="content-header">
      <h1>
        Connections
      </h1>
    </section>
    <section class="content">
      <driconx-callout v-if="!connected"
      type="callout callout-danger"
      icon="fa fa-exclamation-triangle fa-fw"
      title="driconx disconnected!"
      text="Reload the page to try to reconnect to the driconx websocket.">
    </driconx-callout>
    <driconx-callout v-if="bindings.length == 0"
    type="callout callout-danger"
    icon="fa fa-ban fa-fw"
    title="No registered bindings.">
  </driconx-callout>

  <driconx-controls :bindings="bindings" v-on:add-connection="connect">
  </driconx-controls>

  <hr />
  <div class="row">
    <div class="col-md-9">
      <driconx-connection v-for="conx in connections"
      :conx="conx"
      v-on:disconnect="disconnect"
      v-on:connect="connect">
    </driconx-connection>
  </div>

  <driconx-aggregs class="col-md-3" :connections="connections">
  </driconx-aggregs>
</div>
</section>
</section>
</template>

<script>
import WebSocketClient from 'websocket.js'
import Callout from './components/callout.vue'
import Controls from './components/controls.vue'
import Connection from './components/connection.vue'
import Aggregs from './components/aggregs.vue'

export default {
  name: 'driconx',
  components: {
    'driconx-callout': Callout,
    'driconx-controls': Controls,
    'driconx-connection': Connection,
    'driconx-aggregs': Aggregs
  },
  computed: {
    drichost () {
      return this.$store.state.drichost
    }
  },
  methods: {
    disconnect (connection) {
      // Click on disconnect button
      connection.connecting = true
      window.$.ajax({
        url: 'http://' + this.drichost + '/driconx/disconnect',
        method: 'post',
        data: JSON.stringify(connection)
      }).done(function (data, textStatus, jqXHR) {
        connection.connecting = false
        connection.connected = false
        connection.status = null
      }).fail(function (jqXHR, textStatus, errorThrown) {
        connection.connecting = false
        connection.connected = true
        connection.status = errorThrown
      })
    },
    connect (connection) {
      connection.connecting = true
      window.$.ajax({
        url: 'http://' + this.drichost + '/driconx/new',
        method: 'put',
        data: JSON.stringify(connection)
      }).done(function (data, textStatus, jqXHR) {
        connection.connecting = false
        connection.connected = true
        connection.status = null
      }).fail(function (jqXHR, textStatus, errorThrown) {
        connection.connecting = false
        connection.connected = false
        connection.status = errorThrown
      })
    }

  },
  data () {
    return {
      connected: false,
      connections: [],
      bindings: [],
      driconxws: null
    }
  },
  beforeCreate () {
    let drichost = this.$store.state.drichost
    let self = this
    this.ws = new WebSocketClient('ws://' + drichost + '/driconx/ws')
    this.ws.onmessage = function (event) {
      var data = JSON.parse(event.data)
      self.connected = true
      self.connections = data

      for (var i = 0; i < self.connections.length; i++) {
        var c = self.connections[i]
        if (!('hover' in c)) c['hover'] = false
      }
    }
    this.ws.onclose = function () {
      self.connected = false
    }
    window.$.getJSON('http://' + drichost + '/driconx/bindings', function (bindings) {
      self.bindings = bindings
    })
  }
}
</script>

<style>
.driconx-pointer {
  cursor: pointer;
}

.driconx-move {
  cursor: move;
}

.driconx-blink {
  animation: driconx-blink linear 0.1s 4;
  animation-direction: alternate;
  opacity:0;
}

.box.box-success > .driconx-blink{
  background-color:green;
}

.box.box-warning > .driconx-blink{
  background-color:orange;
}

.box.box-danger > .driconx-blink{
  background-color:red;
}

@keyframes driconx-blink{
  100% {opacity: 0.5}
}
</style>