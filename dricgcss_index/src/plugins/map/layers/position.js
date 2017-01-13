/* eslint-disable no-unused-vars */

import ol from 'openlayers'
import WebSocketDatasource from 'websocket-datasource'
import Config from '../../../config'
import Url from 'url'
import randomstring from 'randomstring'
import iconUrl from '../assets/plane_icon_nose_up.png'

const sid = randomstring.generate()
const urlTemplate = Url.format({
  protocol: Config.ws,
  hostname: Config.hostname,
  port: Config.port,
  pathname: '/datasource',
  search: `?s=map-position/global$__ESID__&p=10&sid=${sid}`
})

const PositionLayer = function () {
  const fields = ['lat', 'lon', 'alt', 'heading']
  let esid = null
  let ws = null
  let position = fields.reduce((a, v, i) => Object.assign(a, {[v]: 0}), {})

  const icon = new ol.style.Icon({
    src: iconUrl,
    scale: 0.2,
    color: 'orange'
  })
  var feature = new ol.Feature({
    name: 'UAV',
    geometry: new ol.geom.Point(ol.proj.fromLonLat([position.lon, position.lat]))
  })
  feature.setStyle(function (resolution) {
    const style = new ol.style.Style({
      // geometry: new ol.geom.Point(ol.proj.fromLonLat([position.lon, position.lat])),
      image: icon
    })
    return [style]
  })
  this.source = new ol.source.Vector({features: [feature]})

  function newWs (esid) {
    if (ws !== null) { ws.close() }
    const url = urlTemplate.replace('__ESID__', esid)
    ws = new WebSocketDatasource(url)
    ws.onmessage = function (m) {
      const view = new DataView(m.data)
      position = fields.reduce((a, v, i) => Object.assign(a, {[v]: view.getFloat64(i * 8)}), {})
      position.lat = position.lat / 1e7
      position.lon = position.lon / 1e7
      position.alt = position.alt / 1e7
      position.heading = position.heading * Math.PI / 180.0
      feature.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([position.lon, position.lat])))
      icon.setRotation(position.heading)
    }
  }

  Object.defineProperty(this, 'esid', {
    set (value) {
      esid = value
      newWs(esid)
    },
    get: () => esid
  })

  this.destroy = function () {
    if (ws !== null) {
      console.log('destroy')
      ws.close()
    }
  }
}

export default PositionLayer
