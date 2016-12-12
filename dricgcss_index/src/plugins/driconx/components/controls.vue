<template>
  <div class="row">
    <div class="col-md-12">
      <form class="connection form-inline">

        <div class="form-group">
          <label for="connectionType">Connection type: </label>
          <select class="form-control" v-model="newConnection.type" name="connectionType" required>
            <option>UDP</option>
            <option>TCP</option>
          </select>
        </div>

        <div class="form-group">
          <label for="host">Host: </label>
          <input type="text" class="form-control" v-model="newConnection.host" name="host" required />
        </div>

        <div class="form-group">
          <label for="port">Port: </label>
          <input type="text" class="form-control" v-model="newConnection.port" name="port" required />
        </div>

        <div class="form-group">
          <label for="binding">Binding: </label>
          <select class="form-control" v-model="newConnection.binding" name="binding" v-bind:disabled="newConnection.multibinding" required>
            <option v-for="binding in bindings">{{binding}}</option>
          </select>
        </div>

        <!--<div class="checkbox">
          <label>
            <input type="checkbox" v-model="newConnection.multibinding" name="multibinding" disabled />
            Multi-binding connection
          </label>
        </div>-->

        <button type="submit" class="btn btn-success" v-on:click="add">Add</button>

        <div class="checkbox">
          <label>
            <input type="checkbox" v-model="active_only" name="active_only" />
            Show active connections only
          </label>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'driconx-controls',
  props: ['bindings'],
  methods: {
    add (ev) {
      ev.preventDefault()
      let newConnx = window.$.extend(true, {}, this.newConnection)
      this.$emit('add-connection', newConnx)
    }
  },
  data () {
    return {
      active_only: false,
      newConnection: {
        type: 'UDP',
        host: '127.0.0.1',
        port: 14551
      }
    }
  }
}
</script>

<style>

</style>
