<template>
  <section class="content body page" id="vapp-charts">
    <div style="width:100%; height:400px" id="samples-chart" @mousewheel="zoom" @mousemove="pan" @mousedown="mousedown" @mouseup="mouseup" @mouseexit="mouseup" @mouseenter="mouseup">
    </div>
    <div class="btn-group">
      <button class="btn btn-default" data-toggle="button" title="Pause" @click="pause"><i class="fa fa-pause"></i></button>
      <button class="btn btn-default" title="Clear" @click="clear"><i class="fa fa-eraser"></i></button>
    </div>
    <div class="btn-group">
      <button class="btn btn-default" title="Zoom auto" @click="zoomAuto"><i class="fa fa-arrows-alt"></i></button>
      <button class="btn btn-default" title="Zoom +" @click="zoomPlus"><i class="fa fa-search-plus"></i></button>
      <button class="btn btn-default" title="Zoom -" @click="zoomMinus"><i class="fa fa-search-minus"></i></button>
    </div>
    <div class="btn-group">
      <button class="btn btn-default refresh-chart-source-tree-button" title="Reload list" @click="fetchDatasources"><i class="fa fa-refresh"></i></button>
    </div>
    <span class="form-inline">
      <span class="form-group">
        <input class="form-control search-chart-source-tree" type="text" placeholder="Search for time serie" v-model="search" />
      </span>
      <span class="form-group pull-right">
        <label>X axis</label>
        <select class="form-control x-axis-zoom" v-model="xaxis">
          <option value="10">10 seconds</option>
          <option value="20">20 seconds</option>
          <option value="30">30 seconds</option>
          <option value="40">40 seconds</option>
          <option value="50">50 seconds</option>
          <option value="60">1 minute</option>
          <option value="120">2 minutes</option>
          <option value="180">3 minutes</option>
          <option value="300">5 minutes</option>
          <option value="600">10 minutes</option>
          <option value="1200">20 minutes</option>
        </select>
      </span>
    </span>
    <div class="box col-md-12">
      <div class="box-body">
        <tree-view :value="sources" :search="search" @checkedplot="checkedplot" @uncheckedplot="uncheckedplot"></tree-view>
      </div>
    </div>
  </section>
</template>
<script>
import TreeView from './treeview'
import $ from 'jquery'
import Url from 'Url'
import Config from '../../config'
import Plot from './Plot'

function toSourceTree (raw) {
  const out = []
  const groups = {}
  for (let name of raw) {
    const [parent, sub] = name.split('/')
    const [variable, esid] = sub.split('$')
    if (!(parent in groups)) {
      groups[parent] = {}
    }
    if (!(variable in groups[parent])) {
      groups[parent][variable] = []
    }
    groups[parent][variable].push(esid)
  }
  for (let parent in groups) {
    const children = []
    for (let child in groups[parent]) {
      const alternatives = []
      for (let alt of groups[parent][child].sort()) {
        alternatives.push({
          text: alt,
          selected: false
        })
      }
      children.push({
        text: child,
        alternatives
      })
    }
    out.push({
      selected: false,
      children,
      text: parent
    })
  }
  return out
}

export default {
  components: {
    'tree-view': TreeView
  },
  data () {
    return {
      search: '',
      xaxis: '10',
      sources: [],
      selectedSources: [],
      plotRegistry: null
    }
  },
  watch: {
    xaxis () {
      if (this.plotRegistry) {
        this.plotRegistry._data.xaxis = this.xaxis
      }
    },
    selectedSources () {
      /* eslint-disable */
      if (this.plotRegistry === null) {
        this.plotRegistry = Plot.make('#samples-chart')
      }
      this.plotRegistry.update(this.selectedSources.map(s => s.sourceName), this.selectedSources.map(s => s.color))
    }
  },
  methods: {
    zoomAuto: function () {
        if (this.plotRegistry) {
          this.plotRegistry.zoomAuto()
        }
    },
    zoomPlus: function () {
        if (this.plotRegistry) {
          this.plotRegistry.zoomPlus()
        }
    },
    zoomMinus: function () {
        if (this.plotRegistry) {
          this.plotRegistry.zoomMinus()
        }
    },
    pause: function () {
        if (this.plotRegistry) {
          this.plotRegistry.pause()
        }
    },
    clear: function () {
        this.$emit('clear')
    },
    zoom: function(e) {
      if (this.plotRegistry !== null) {
        this.plotRegistry.zoom(e)
      }
    },
    pan: function(e) {
      if (this.plotRegistry !== null) {
        this.plotRegistry.pan(e)
      }
    },
    mousedown: function(e) {
      e.preventDefault()
      if (this.plotRegistry !== null) {
        this.plotRegistry.mousedown(e)
      }
    },
    mouseup: function(e) {
      e.preventDefault()
      if (this.plotRegistry !== null) {
        this.plotRegistry.mouseup(e)
      }
    },
    checkedplot (sourceName, color) {
      this.selectedSources.push({sourceName, color})
    },
    uncheckedplot (target) {
      this.selectedSources.removeIf(s => s.sourceName === target)
    },
    fetchDatasources () {
      const url = Url.format({
        protocol: Config.http,
        hostname: Config.hostname,
        port: Config.port,
        pathname: '/dsws_datasources'
      })
      $.getJSON(url, (json) => {
        this.sources = toSourceTree(json)
      })
    }
  },
  mounted () {
    this.fetchDatasources()
  }
}
</script>
<style>
#samples-chart {
  cursor: ns-resize;
}
</style>
