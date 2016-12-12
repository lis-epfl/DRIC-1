import WebSocketDatasource from 'websocket-datasource'
import Url from 'url'
import { MavWsConfig } from '../../config'

function sourceNameFrom (messageType, fieldName, esid) {
  const prefix = 'mavlink-'
  return `${prefix}${messageType}/${fieldName}$${esid}`
}

const That = function (messageType, fieldName, esid) {
  this.messageType = messageType
  this.fieldName = fieldName
  this.esid = esid
}

const TimeHelper = function (that) {
  let lastTime = null
  let thatLastTime = null

  this.update = function (time) {
    thatLastTime = lastTime
    lastTime = time
  }

  Object.defineProperties(that, {
    lastTime: {
      get: function () { return thatLastTime }
    }
  })
}

export default {
  /**
   * Subscribe to fieldName in messageType for esid.
   * @param  {string} messageType
   * @param  {string} fieldName
   * @param  {string} esid
   * @param  {Function} callback (time, value), this.messageType,
   * this.fieldName, this.esid and this.lastTime
   */
  subscribe (messageType, fieldName, esid, callback) {
    const that = new That(messageType, fieldName, esid)
    const timeHelper = new TimeHelper(that)

    const sourceName = sourceNameFrom(messageType, fieldName, esid)
    const url = Url.format({
      protocol: MavWsConfig.protocol,
      hostname: MavWsConfig.hostname,
      port: MavWsConfig.port,
      pathname: MavWsConfig.pathname,
      search: MavWsConfig.search(sourceName)
    })

    const ws = new WebSocketDatasource(url)
    ws.onmessage = function (message) {
      const view = new DataView(message.data)
      const time = view.getFloat64(0)
      const value = view.getFloat64(8)
      timeHelper.update(time)

      callback.call(that, time, value)
    }
    ws.onclose = function (code) {
      console.warn(`Websocket ${url} closed (${code}).`)
    }

    return () => ws.close()
  }
}
