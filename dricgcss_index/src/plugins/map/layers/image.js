import ol from 'openlayers'

const ImageLayer = function () {
  this.layer = new ol.layer.Image({
    source: new ol.source.ImageStatic({
      url: 'http://example.com/',
      imageExtent: [0, 0, 0, 0]
    })
  })

  let url
  let imageExtent

  Object.defineProperty(this, 'imageUrl', {
    get: () => {
      return url
    },
    set: (value) => {
      console.log(value)
      url = value
      this.layer.setSource(new ol.source.ImageStatic({
        url,
        imageExtent
      }))
    }
  })

  Object.defineProperty(this, 'imageExtent', {
    get: () => {
      return imageExtent
    },
    set: (value) => {
      imageExtent = value
      this.layer.setSource(new ol.source.ImageStatic({
        url,
        imageExtent
      }))
    }
  })
}

export default ImageLayer
