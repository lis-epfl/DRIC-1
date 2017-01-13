<template>
  <div class="box box-primary box-solid"
  v-on:drop="$emit('aggreg-drop', $event)"
  v-on:dragenter="$event.preventDefault()"
  v-on:dragleave="$event.preventDefault()"
  v-on:dragover="$event.preventDefault()">

  <div class="box-header with-border">
    <input type="text" v-model="calias"></input>
    <div class="box-tools pull-right">
      <span type="button" class="btn btn-box-tool" data-toggle="tooltip" title="" data-original-title="reason" v-if="reason !== null">
        <i class="fa fa-question"></i>
      </span>
      <button type="button" class="btn btn-box-tool" data-widget="collapse"><i class="fa fa-minus"></i></button>
    </div>
  </div>

  <div class="box-body">
    <ul>
      <li class="driconx-pointer"
      draggable="true"
      v-for="esid in esidList"
      v-on:dragstart="$emit('startdrag', esid.esid);$event.dataTransfer.setData('application/json',JSON.stringify({esid:esid.esid,systemid:systemid}))"
      v-on:dragend="$emit('enddrag', esid.esid)"
      v-on:mouseenter="esid.connection.hover=true"
      v-on:mouseleave="esid.connection.hover=false">
      {{esid.esid}}
      <span class="label bg-red" v-if="!esid.connection.connected">
        <i class="fa fa-exclamation"></i>
      </span>
    </li>
  </ul>
</div>

<div class="box-footer"
v-if="esidList.length > 1">
<button class="btn btn-danger"
v-on:click="$emit('deaggregate')">
Deaggregate All
</button>
</div>
</div>
</template>

<script>
import hash from 'string-hash'

let warned = false
function setLocalStorageItem (name, value) {
  try {
    window.localStorage.setItem(name, value)
  } catch (e) { warn('localStorage not available') }
}

function getLocalStorageItem (name) {
  try {
    return window.localStorage.getItem(name)
  } catch (e) { warn('localStorage not available') }
}
function warn (message) {
  if (!warned) {
    warned = true
    console.warn(message)
  }
}
function hashkey (esidList) {
  if (Array.isArray(esidList)) {
    return 'aggreg/' + hash(esidList.concat().sort().map(e => e.esid).join(','))
  }
}
setLocalStorageItem()
getLocalStorageItem()

export default {
  props: ['esidList', 'alias', 'reason', 'systemid'],
  watch: {
    'esidList': function () {
      if (this.esidList.length <= 0) {
        this.$emit('empty-aggreg')
      }

      const lsalias = getLocalStorageItem(hashkey(this.esidList))
      if (lsalias !== null && lsalias !== this.calias) {
        this.$nextTick(() => (this.calias = lsalias))
      }
    },
    'calias': function () {
      this.$emit('alias-changed', this.calias)
      if (typeof this.calias !== 'undefined') {
        setLocalStorageItem(hashkey(this.esidList), this.calias)
      }
    }
  },
  data () {
    return { calias: '' }
  },
  mounted () {
    this.calias = this.alias
    const lsalias = getLocalStorageItem(hashkey(this.esidList))
    if (lsalias !== null && lsalias !== this.calias) {
      this.calias = lsalias
      this.$emit('alias-changed', this.calias)
    }
  }
}
</script>

<style>
.box-header input {
  color: initial;
}
</style>
