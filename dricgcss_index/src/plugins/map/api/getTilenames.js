import $ from 'jquery'
import Url from 'url'
import Config from '../../../config'

export const getTilenames = function (cb) {
  const url = Url.format({
    protocol: Config.http,
    hostname: Config.hostname,
    port: Config.port,
    pathname: '/map/maps'
  })
  $.getJSON(url, function (data) {
    cb(data)
  })
}
