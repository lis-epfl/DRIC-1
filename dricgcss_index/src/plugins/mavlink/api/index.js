import $ from 'jquery'
import Url from 'url'
import WebSocketClient from 'websocket-datasource'

import {Config, DatasourceConfig} from '../config'

const API = function () {
  this.getServerTime = function (callback) {
    /** Return server time in seconds */
    const pathname = '/mavlink/time'
    const url = Url.format({protocol: 'http', port: Config.port, hostname: Config.hostname, pathname})
    $.get(url, (r) => callback(r))
  }

  this.createMessageTypeWebsocket = function (esid, messageType) {
    /** create a full message websocket for given esid and message type.
    Frame is a timestamp (double in s) and a json payload */
    const url = Url.format({
      protocol: DatasourceConfig.protocol,
      hostname: DatasourceConfig.hostname,
      port: DatasourceConfig.port,
      pathname: DatasourceConfig.pathname,
      search: DatasourceConfig.search(`mavlink-${messageType}$${esid}`)
    })
    return new WebSocketClient(url)
  }

  this.getUnits = function (callback) {
    const url = Url.format({
      protocol: Config.http,
      hostname: Config.hostname,
      port: Config.port,
      pathname: '/mavlink/units'
    })
    $.getJSON(url, callback)
  }

  this.allHref = function (messageType, esidList = [], paramList = [], from = 0, to = undefined) {
    const query = {
      esid: esidList,
      param: paramList,
      from
    }
    if (typeof to !== 'undefined' && to !== null) {
      query.to = to
    }
    return Url.format({
      protocol: Config.http,
      hostname: Config.hostname,
      port: Config.port,
      pathname: `/mavlink/downloadt/${messageType}`,
      query
    })
  }
}

export default API
