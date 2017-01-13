<template>
  <div class="box">
    <div class="box-body">
      <button v-for="item in customCommands" v-if="item.type==='button'" @click="send(item.command)" class="btn btn-default">{{item.text}}</button>
    </div>
  </div>
</template>
<script>
import CustomCommands from './custom/CustomCommands.json'
import $ from 'jquery'
import Config from '../../config'
import Url from 'url'

export default {
  props: ['esid'],
  data () {
    return {}
  },
  computed: {
    customCommands: function () {
      return CustomCommands
    }
  },
  methods: {
    send (command) {
      const url = Url.format({
        potocol: Config.http,
        hostname: Config.hostname,
        port: Config.port,
        pathname: `/mavlink/command/${this.esid}/${command[0]}`
      })
      $.post(url, {p: command.slice(3)})
    }
  }
}
</script>
<style>
</style>
