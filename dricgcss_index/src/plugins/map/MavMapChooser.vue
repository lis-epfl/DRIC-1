<template>
  <div class="box">
    <div class="box-body">
      <label>Select a map layer:</label>
      <select v-model="selectedTilename" class="form-control">
        <option disabled="disabled">
          Web providers
        </option>
        <option v-for="tilename in defaultTilenames" :value="tilename">
          {{tilename}}
        </option>
      </select>
      <label>Select a map overlay:</label>
      <select v-model="selectedOverlay" class="form-control">
        <option :value="null">
          No overlay
        </option>
        <option v-for="tilename in tilenames" :value="tilename">
          {{tilename}}
        </option>
      </select>
    </div>
  </div>
</template>
<script>
import * as types from './types'
import API from './api'
const api = new API()
export default {
  data () {
    return {
      tilenames: [],
      defaultTilenames: ['Bing', 'Stamen', 'OSM'],
      selectedTilename: 'Bing',
      selectedOverlay: null
    }
  },
  watch: {
    selectedTilename () {
      this.$store.commit(types.MAP_LAYER, this.selectedTilename)
    },
    selectedOverlay () {
      api.getInfos(this.selectedOverlay, o => this.$store.commit(types.MAP_OVERLAY, o))
    }
  },
  mounted () {
    api.getTilenames(t => (this.tilenames = t))
  }
}
</script>
<style>
</style>
