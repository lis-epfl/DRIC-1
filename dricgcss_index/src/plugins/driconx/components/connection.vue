<template>
  <div class="col-md-3"  v-if="!active_only || conx.connecting || conx.connected">
    <div class="box"
    v-bind:class="conx.connecting?'box-warning':(conx.connected?'box-success':'box-danger')">
    <div class="box-header with-border">
      <h3 class="box-title">
        {{conx.type}}://{{conx.host}}:{{conx.port}}
        <span class="small">[{{conx.binding}}]</span>
      </h3>
      <div class="box-tools pull-right">
        <button type="button" class="btn btn-box-tool" v-if="!conx.connecting && !conx.connected" v-on:click="$emit('deleteconx', conx)">
          <i class="fa fa-times"></i>
        </button>
      </div>
    </div>
    <div class="box-body">
      <p><b>{{typeof conx.systems === 'undefined' ? 'No' : conx.systems.length}}</b> systems connected: </p>
      <ul v-if="typeof conx.systems !== 'undefined'">
        <li v-for="systemid in conx.systems"><a href="#">{{systemid}}</a></li>
      </ul>
    </div>
    <div class="box-header with-border">
      <button type="button" class="btn btn-danger" v-on:click="$emit('disconnect', conx)" v-if="conx.connected">
        Disconnect
      </button>
      <button type="button" class="btn btn-success" v-on:click="$emit('connect', conx)" v-bind:disabled="conx.connecting" v-else>
        Connect
      </button>
      <i class="fa fa-cog fa-spin" v-if="conx.connecting"></i>
      <span class="text-muted">{{conx.status}}</span>
    </div>
    <div class="overlay driconx-blink driconx-blink-green" v-if="conx.hover">

    </div>
  </div>
</div>
</template>
<script>
export default {
  props: ['active_only', 'conx']
}
</script>
