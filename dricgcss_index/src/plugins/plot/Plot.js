/* eslint-disable */
import Vue from 'vue'
import ControllableAxis from './ControllableAxis'
import FixedLengthAxis from './FixedLengthAxis'
import randomstring from 'randomstring'
var self = {}
var sid = randomstring.generate()
var WebSocketDatasource = require('websocket-datasource')

import Config from '../../config'
import Url from 'url'

var maxTime = 0

function PlotRegistry () {
  var templateUrl = Url.format({
    protocol: Config.ws,
    hostname: Config.hostname,
    port: Config.port,
    pathname: '/datasource',
    search: `?s=__SOURCE__&p=10&sid=${sid}`
  })
  var sources = {}
  var colors = []
  var colorsValid = false
  var self = this

  this.colorProvider = null
  this.visiblePoints = 3000
  this.offset = 0

  this.getColors = function () {
    if (!colorsValid) {
      if (this.colorProvider !== null) {
        colors = []
        for (let source in sources) {
          colors.push(this.colorProvider.getColorForSource(source))
        }
        colorsValid = true
      }
    }
    return colors
  }

  this.update = function (updatedSources, colors) {
    // Delete open sources which are not in updated sources
    for (let source in sources) {
      if (updatedSources.indexOf(source) < 0) {
        sources[source].close()
        delete sources[source]
        invalidate()
      }
    }

    // Add updates sources which are not in open sources
    for (var i = 0; i < updatedSources.length; i++) {
      var source = updatedSources[i]
      if (!(source in sources)) {
        var url = templateUrl.replace('__SOURCE__', source)
        sources[source] = new RealTimePlotUpdate(url, 300)
        invalidate()
      }
    }

    self._data = Object.assign(self._data || {}, {colors})
  }

  this._pause_start = function () {
    var i = 0
    var forcedStart = []
    for (let source in sources) {
      var res = sources[source].res
      forcedStart[i] = {}
      forcedStart[i].start = Math.max(res.length - self.visiblePoints - self.offset, 0)
      forcedStart[i].end = Math.min(forcedStart[i].start + self.visiblePoints, res.length)
      i++
    }
    return forcedStart
  }

  this._plotdata = function (forced) {
    var data = []
    var i = 0
    for (let source in sources) {
      var res = sources[source].res
      var start = Math.max((typeof forced === 'undefined' ? Math.max(res.length - self.visiblePoints, 0) : forced[i].start) - self.offset, 0)
      var end = Math.min(typeof forced === 'undefined' ? (start + self.visiblePoints) : forced[i].end - self.offset, res.length, res.length)
      data.push(res.slice(start, end))
      i++
    }
    return data
  }

  function invalidate () {
    colorsValid = false
  }
}

function RealTimePlotUpdate (url, maxPoint) {
  var socket = null
  this.res = []
  var self = this
  open_socket()

  function open_socket () {
    socket = new WebSocketDatasource(url)
    socket.onmessage = recv
    socket.onopen = request
    socket.binaryType = 'arraybuffer'
  }

  function recv (msg) {
    var view = new DataView(msg.data)
    for (var i = 0; i < view.byteLength; i += 16) {
      var time = view.getFloat64(i)
      var mag = view.getFloat64(i + 8)
      if (time > maxTime) {
        maxTime = time
      }
      update(time, mag)
    }
    //var filereader = new FileReader()
    //filereader.onload = function () {
    //    var split = this.result.split(' ')
    //    var time = parseFloat(split[0])
    //    var mag = parseFloat(split[1])
    //    update(time, mag)
    //}
    //filereader.readAsBinaryString(msg.data)
  }

  function update (time, mag) {
    //if (self.res.length > maxPoint) {
    //    self.res = self.res.slice(1)
    //}
    self.res.push([time, mag])
  }

  function request() {
    if (socket !== null && socket.readyState === WebSocket.OPEN) {
    }
  }

  this.close = function () {
    socket.close()
  }
}
self.make = function (selector) {
  var maxTimePause
  var plotRegistry = new PlotRegistry()
  var options = {
    yaxis: new ControllableAxis(1.5, -1.5, function () { return plot ? plot.getYAxes()[0] : { min: 0, max: 0 }; }),
    xaxis: new FixedLengthAxis(function () { return plotRegistry._data ? plotRegistry._data.xaxis : 0; }, function () { return plotRegistry._data && plotRegistry._data.paused?maxTimePause:maxTime; })
  }

  //var rng = new RealTimePlotUpdate('ws://' + host + '/datasource?s=Samples/rng&p=17', 300)
  //var sin = new RealTimePlotUpdate('ws://' + host + '/datasource?s=Samples/sin&p=28', 300 / 28 * 17)

  var pauseData = []
  var plot = null

  redraw()

  /**
  Return range of data in the given dimension.
  Return {min: min, max: max}
  */
  function rangeOf(data, dimension) {
    var range = { min: null, max: null }
    for (var serieIndex = 0; serieIndex < data.length; serieIndex++) {
      var serie = data[serieIndex]
      for (var pointIndex = 0; pointIndex < serie.length; pointIndex++) {
        var point = serie[pointIndex]
        if (range.min == null) {
          range.min = point[dimension]
        } else if (point[dimension] < range.min) {
          range.min = point[dimension]
        }
        if (range.max == null) {
          range.max = point[dimension]
        } else if (point[dimension] > range.max) {
          range.max = point[dimension]
        }
      }
    }
    return range
  }
  var pauseStart
  function redraw() {
    window.$(selector).data('plot', plot)
    var plotdata

    if (typeof plotRegistry._data !== 'undefined' && plotRegistry._data.paused) {
      plotdata = plotRegistry._plotdata(pauseStart)
    } else {
      plotdata = plotRegistry._plotdata()
    }

    options.xaxis.update()
    if (typeof plotRegistry._data !== 'undefined') {
      options.colors = plotRegistry._data.colors
    }

    plot = window.$.plot(selector, plotdata, options)

    // Animation frame won't work here
    setTimeout(redraw, 70)
  }

  function copyRealtime() {
    var data = plotRegistry._plotdata()
    pauseData = []
    for (var i = 0; i < data.length; i++) {
      pauseData.push(data[i].slice(0))
    }
    pauseStart = plotRegistry._pause_start()
    maxTimePause = maxTime
  }

  plotRegistry._data = {}
  plotRegistry._data.mouseButtonDown = false
  plotRegistry._data.cursor = 'default'
  plotRegistry._data.xaxis = 60
  plotRegistry._data.colors = []
  plotRegistry._data.paused = false
  plotRegistry.zoomAuto = options.yaxis._d.zoom.auto
  plotRegistry.zoomPlus = options.yaxis._d.zoom.plus
  plotRegistry.zoomMinus = options.yaxis._d.zoom.minus
  plotRegistry.zoom = options.yaxis._d.zoom.mousewheel
  plotRegistry.mousedown = () => {plotRegistry._data.mouseButtonDown = true}
  plotRegistry.mouseup = () => {
    plotRegistry._data.mouseButtonDown = false
    options.yaxis._d.pan.mousedragstop()
  }
  plotRegistry.pause = () => {
      plotRegistry._data.paused = !plotRegistry._data.paused
      copyRealtime()
  }
  plotRegistry.pan = (e) => {
    if (plotRegistry._data.mouseButtonDown) {
      options.yaxis._d.pan.mousedrag(e)
    }
  }
/*
  var vappCharts = new Vue({
    el: '#vapp-charts',
    data: {
      cursor: 'default',
      mousedown: false,
      xaxis: 60
    },
    methods: {
      pause: function (e) {
        paused = !paused
        copyRealtime()
      },
      startRecord: function () { },
      pan: function (e) {
        if (this.mouseButtonDown) {
          this.cursor = 'all-scroll'
          options.yaxis._d.pan.mousedrag(e)
        } else {
          this.cursor = 'default'
        }
      },
      zoomAuto: options.yaxis._d.zoom.auto,
      zoomPlus: options.yaxis._d.zoom.plus,
      zoomMinus: options.yaxis._d.zoom.minus,
      zoom: options.yaxis._d.zoom.mousewheel,
      mousedown: function (e) { e.preventDefault(); this.mouseButtonDown = true; },
      mouseup: function (e) {
        e.preventDefault(); this.mouseButtonDown = false
        options.yaxis._d.pan.mousedragstop()
      },
      clear: function () { plotRegistry.clear(); }
    }
  })
*/
  /************************************
  * REAL TIME PLOT UPDATE             *
  *************************************/
  var paused = false
  var origin_date = Date.now()
  return plotRegistry
}

export default self
