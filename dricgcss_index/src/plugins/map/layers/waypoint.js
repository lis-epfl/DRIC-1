import ol from 'openlayers'

const WaypointLayer = function () {
  let waypoints
  let selectedWaypoint

  const features = new ol.Collection()
  this.source = new ol.source.Vector({features})

  function updateFeatures () {
    features.clear()
    for (let waypoint of waypoints) {
      console.log(waypoint.current)
      const name = 'Waypoint#' + waypoint.seq
      const feature = new ol.Feature({
        name,
        geometry: new ol.geom.Point(ol.proj.fromLonLat([waypoint.y, waypoint.x]))
      })
      feature.setStyle(new ol.style.Style({
        text: new ol.style.Text({
          text: '#' + waypoint.seq,
          scale: 2,
          font: waypoint.current === 1 ? 'bold 10px sans-serif' : '10px sans-serif'
        }),
        geometry: feature.getGeometry(),
        image: new ol.style.Circle({
          fill: new ol.style.Fill({
            color: waypoint === selectedWaypoint ? 'rgba(75,57,221,0.8)' : 'rgba(221,75,57,0.8)'
          }),
          stroke: new ol.style.Stroke({
            color: waypoint.current === 1 ? 'black' : 'rgb(225,75,57)',
            width: waypoint.current === 1 ? 2 : 1.25
          }),
          radius: 20
        }),
        fill: new ol.style.Fill({
          color: 'rgba(255,255,255,0.4)'
        }),
        stroke: new ol.style.Stroke({
          color: '#3399CC',
          width: 1.25
        })
      }))
      feature.getGeometry().on('change', function () {
        [waypoint.y, waypoint.x] = ol.proj.toLonLat(feature.getGeometry().getCoordinates())
        // waypoint.updated()
      })
      features.push(feature)
    }
  }

  Object.defineProperty(this, 'waypoints', {
    set (value) {
      waypoints = value
      updateFeatures()
    },
    get: () => waypoints
  })
  Object.defineProperty(this, 'selectedWaypoint', {
    set (value) {
      selectedWaypoint = value
      updateFeatures()
    },
    get: () => selectedWaypoint
  })

  const self = this
  this.Drag = function () {
    ol.interaction.Pointer.call(this, {
      handleDownEvent: self.Drag.prototype.handleDownEvent,
      handleDragEvent: self.Drag.prototype.handleDragEvent,
      handleMoveEvent: self.Drag.prototype.handleMoveEvent,
      handleUpEvent: self.Drag.prototype.handleUpEvent
    })

    /**
    * @type {ol.Pixel}
    * @private
    */
    this.coordinate_ = null

    /**
    * @type {string|undefined}
    * @private
    */
    this.cursor_ = 'pointer'

    /**
    * @type {ol.Feature}
    * @private
    */
    this.feature_ = null

    /**
    * @type {string|undefined}
    * @private
    */
    this.previousCursor_ = undefined
  }
  ol.inherits(this.Drag, ol.interaction.Pointer)

  /**
  * @param {ol.MapBrowserEvent} evt Map browser event.
  * @return {boolean} `true` to start the drag sequence.
  */
  this.Drag.prototype.handleDownEvent = function (evt) {
    var map = evt.map

    var feature = map.forEachFeatureAtPixel(evt.pixel, function (feature, layer) {
      return feature
    })

    if (feature) {
      this.coordinate_ = evt.coordinate
      this.feature_ = feature
    }

    return !!feature
  }

  /**
  * @param {ol.MapBrowserEvent} evt Map browser event.
  */
  this.Drag.prototype.handleDragEvent = function (evt) {
    var map = evt.map

    /* eslint-disable no-unused-vars */
    var feature = map.forEachFeatureAtPixel(evt.pixel, function (feature, layer) {
      return feature
    })

    var deltaX = evt.coordinate[0] - this.coordinate_[0]
    var deltaY = evt.coordinate[1] - this.coordinate_[1]

    var geometry = /** @type {ol.geom.SimpleGeometry} */
    (this.feature_.getGeometry())
    geometry.translate(deltaX, deltaY)

    this.coordinate_[0] = evt.coordinate[0]
    this.coordinate_[1] = evt.coordinate[1]
  }

  /**
  * @param {ol.MapBrowserEvent} evt Event.
  */
  this.Drag.prototype.handleMoveEvent = function (evt) {
    if (this.cursor_) {
      var map = evt.map
      var feature = map.forEachFeatureAtPixel(evt.pixel, function (feature, layer) {
        return feature
      })
      var element = evt.map.getTargetElement()
      if (feature) {
        if (element.style.cursor !== this.cursor_) {
          this.previousCursor_ = element.style.cursor
          element.style.cursor = this.cursor_
        }
      } else if (this.previousCursor_ !== undefined) {
        element.style.cursor = this.previousCursor_
        this.previousCursor_ = undefined
      }
    }
  }

  /**
  * @param {ol.MapBrowserEvent} evt Map browser event.
  * @return {boolean} `false` to stop the drag sequence.
  */
  this.Drag.prototype.handleUpEvent = function (evt) {
    this.coordinate_ = null
    this.feature_ = null
    return false
  }
}

export default WaypointLayer
