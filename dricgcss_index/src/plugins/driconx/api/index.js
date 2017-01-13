import $ from 'jquery'
import Url from 'url'
import Config from '../../../config'
import WebSocketClient from 'websocket.js'

const API = function () {
  function urlFormatter (pathname) {
    return Url.format({
      protocol: Config.http,
      hostname: Config.hostname,
      port: Config.port,
      pathname: pathname
    })
  }

  this.disconnect = function (connection, cbDone, cbFail) {
    const url = urlFormatter('/driconx/disconnect')
    $.ajax({
      url: url,
      method: 'post',
      data: JSON.stringify(connection)
    })
    .done(cbDone)
    .fail(cbFail)
  }

  this.connect = function (connection, cbDone, cbFail) {
    const url = urlFormatter('/driconx/new')
    // Should be PUT /driconx/connections for REST
    $.ajax({
      url: url,
      method: 'put',
      data: JSON.stringify(connection)
    })
    .done(cbDone)
    .fail(cbFail)
  }

  this.deleteconx = function (connection, cbDone, cbFail) {
    const url = urlFormatter('/driconx/delete')
    $.ajax({
      url: url,
      method: 'post', // Should be DELETE
      data: JSON.stringify(connection)
    })
    .done(cbDone)
    .fail(cbFail)
  }

  this.getBindings = function (callback) {
    window.$.getJSON(urlFormatter('/driconx/bindings'), callback)
  }

  this.getWebSocket = function () {
    const url = Url.format({
      protocol: Config.ws,
      hostname: Config.hostname,
      port: Config.port,
      pathname: '/driconx/ws'
    })
    return new WebSocketClient(url)
  }
}

export default API
