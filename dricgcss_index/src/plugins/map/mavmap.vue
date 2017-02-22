<template>
  <div id="mapcontainer">
    {{layerName}}
    <div id="map">
    </div>
  </div>
</template>
<script>
import ol from 'openlayers'
import MapConfig from './config'
import * as types from './types'
import PositionLayer from './layers/position'
import WaypointLayer from './layers/waypoint'
import ImageLayer from './layers/image'

export default {
  props: ['esid', 'waypoints', 'selectedWaypoint'],
  data () {
    return {
      layer: null,
      map: null,
      positionLayer: new PositionLayer(),
      waypointLayer: new WaypointLayer(),
      imageLayer: new ImageLayer()
    }
  },
  computed: {
    layerName () {
      const maplayer = this.$store.getters[types.GET_MAP_LAYER]
      if (typeof maplayer === 'undefined') {
        return 'Bing'
      }
      return maplayer
    },
    overlay () {
      return this.$store.getters[types.GET_MAP_OVERLAY]
    }
  },
  watch: {
    layerName () {
      this.layer.setSource(this.layerSource())
      this.$nextTick(() => this.map.updateSize())
    },
    overlay () {
      const [oxmin, oymin, oxmax, oymax] = this.overlay.imageExtent
      const [xmin, ymin] = ol.proj.fromLonLat([oxmin, oymin])
      const [xmax, ymax] = ol.proj.fromLonLat([oxmax, oymax])
      this.imageLayer.imageUrl = this.overlay.url
      this.imageLayer.imageExtent = [xmin, ymin, xmax, ymax]
    },
    esid () {
      this.positionLayer.esid = this.esid
    },
    waypoints () {
      this.waypointLayer.waypoints = this.waypoints
    },
    selectedWaypoint () {
      this.waypointLayer.selectedWaypoint = this.selectedWaypoint
    }
  },
  methods: {
    layerSource (force) {
      switch (force || this.layerName) {
        case 'Stamen':
          return new ol.source.Stamen({layer: 'terrain'})
        case 'Bing':
          return new ol.source.BingMaps({
            key: MapConfig.providers.bing.key,
            imagerySet: ['AerialWithLabels'],
            maxZoom: 19
          })
        case 'OSM':
        default:
          return new ol.source.OSM()
      }
    }
  },
  mounted () {
    this.positionLayer.esid = this.esid
    this.layer = new ol.layer.Tile({
      source: this.layerSource('Bing')
    })
    const positionLayer = new ol.layer.Vector({
      source: this.positionLayer.source
    })
    const waypointLayer = new ol.layer.Vector({
      source: this.waypointLayer.source
    })

    this.waypointLayer.waypoints = this.waypoints
    this.waypointLayer.selectedWaypoints = this.selectedWaypoints
    this.map = new ol.Map({
      interactions: ol.interaction.defaults().extend([new this.waypointLayer.Drag()]),
      target: 'map',
      layers: [ this.layer, positionLayer, this.imageLayer.layer, waypointLayer ],
      view: new ol.View({
        center: ol.proj.fromLonLat([6.515357, 46.491475]),
        zoom: 12
      })
    })
    this.map.getView().on('change:center', function () {
      const [y, x] = ol.proj.toLonLat(this.map.getView().getCenter())
      this.$emit('mapcenter', {x, y})
    }.bind(this))

    // if openlayers is not nice -> we have to update things manually
    // require('set-interval-n')(() => this.map.updateSize(), 200, 10)
    let i = 0
    const interval = setInterval(() => {
      this.map.updateSize()
      if (++i === 10) {
        clearInterval(interval)
      }
    }, 200)
    // window.setTimeout(() => this.map.updateSize(), 200)

    window.addEventListener('resize', () => this.map.updateSize())
  },
  beforeDestroy () {
    this.positionLayer.destroy()
  }
}
</script>
<style lang="less">
/*@import "../../../node_modules/openlayers/dist/ol.css";*/
#map, #mapcontainer {
  height: 100%;
}
</style>
