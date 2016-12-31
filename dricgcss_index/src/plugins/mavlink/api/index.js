import $ from 'jquery'
import Url from 'url'
import WebSocketClient from 'websocket-datasource'
import WebSocketJs from 'websocket.js'

import {Config, DatasourceConfig} from '../config'

const ACKAPI = function () {
  const url = Url.format({
    protocol: Config.ws,
    hostname: Config.hostname,
    port: Config.port,
    pathname: '/mavlink/command/ack'
  })

  const websocket = new WebSocketJs(url, 'CMD_ACK')
  const cbsTimeouts = {}
  const cbsAcknowledge = {}
  const timers = {}

  websocket.onmessage = function (msg) {
    const [command, argument] = msg.data.split(/:(.+)?/, 2)
    console.log(command, argument)
    switch (command) {
      case 'sub':
        window.clearTimeout(timers[argument])
        timers[argument] = window.setTimeout(function () {
          websocket.send(`unsub:${argument}`)
          cbsTimeouts[argument]
        }, 30000)
        break
      case 'unsub':
        delete cbsTimeouts[argument]
        delete cbsAcknowledge[argument]
        delete timers[argument]
        break
      case 'msg':
        const [ackid, status] = argument.split(/:(.+)?/, 2)
        window.clearTimeout(timers[ackid])
        cbsAcknowledge[ackid](status)
        websocket.send(`unsub:${ackid}`)
        break
      default:
        console.warn(command, argument)
    }
  }

  this.subscribe = function (ackid, cbAcknowledge, cbTimeout) {
    websocket.send(`sub:${ackid}`)
    cbsTimeouts[ackid] = cbTimeout
    cbsAcknowledge[ackid] = cbAcknowledge
    timers[ackid] = window.setTimeout(function () {
      websocket.send(`unsub:${ackid}`)
      cbTimeout()
    }, 30000)
  }
}

const API = function () {
  const ack = new ACKAPI()
  this.getServerTime = function (callback) {
    /** Return server time in seconds */
    const pathname = '/mavlink/time'
    const url = Url.format({protocol: 'http', port: Config.port, hostname: Config.hostname, pathname})
    return $.get(url, (r) => callback(r))
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
    return $.getJSON(url, callback)
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

  this.getAvailableCommands = function (esids, callback) {
    const calls = []
    let commands = []
    console.log(esids)
    // mergedArray.filter((e, i) =>  commands.indexOf(e) === i);
    for (let esid of esids) {
      const url = Url.format({
        protocol: Config.http,
        hostname: Config.hostname,
        port: Config.port,
        pathname: `/driconx/${esid}/cmd`
      })
      calls.push($.getJSON(url, callback))
    }
    console.log(calls)
    $.when.apply(null, calls).then(function () {
      // Concatenate commands
      for (let arg of arguments) {
        if (typeof arg !== 'undefined') {
          commands = commands.concat(arg[0])
        }
      }
      // Remove doublons
      commands.filter((e, i) => commands.indexOf(e) === i)
    })
  }

  this.sendCommand = function (esid, command, parameters, cbAcknowledge, cbTimeout) {
    if (typeof cbAcknowledge === 'undefined') {
      cbAcknowledge = function () {}
    }
    if (typeof cbTimeout === 'undefined') {
      cbTimeout = function () {}
    }

    const url = Url.format({
      protocol: Config.http,
      hostname: Config.hostname,
      port: Config.port,
      pathname: `/mavlink/command/${esid}/${command}`
    })
    return $.post(url, {p: parameters}, (ackid) => ack.subscribe(ackid, cbAcknowledge, cbTimeout))
  }
}

export default API
