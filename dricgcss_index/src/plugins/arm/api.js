import Config from '../../config'
import Url from 'url'
import WebSocketClient from 'websocket.js'
import $ from 'jquery'

const Subscriber = function (esid) {
  this.callback = () => {}
  const ws = new WebSocketClient(Url.format({
    protocol: Config.ws,
    hostname: Config.hostname,
    port: Config.port,
    pathname: '/quickarm/ws',
    query: {esid}
  }))
  ws.onmessage = (m) => this.callback(esid, m.data === '1')
}

const API = function () {
  function urlFormatter (pathname, esid) {
    return Url.format({
      protocol: Config.http,
      hostname: Config.hostname,
      port: Config.port,
      pathname: `/quickarm/${pathname}`,
      query: {esid}
    })
  }

  const subscribers = {}

  this.subscribe = function (esid, callback) {
    if (!(esid in subscribers)) {
      subscribers[esid] = new Subscriber(esid)
    }
    subscribers[esid].callback = callback
  }
  this.unsubscribe = function (esid) {
    subscribers[esid].disconnect()
    delete subscribers[esid]
  }

  this.arm = function (esid) {
    $.get(urlFormatter('arm', esid))
  }

  this.disarm = function (esid) {
    $.get(urlFormatter('disarm', esid))
  }
}

export default API
