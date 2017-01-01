import Url from 'url'
import Config from '../../../config'
import WebSocketJs from 'websocket.js'

const ParaP = function (esid) {
  const self = this
  function sendto (url) {
    const ws = new WebSocketJs(url, 'ParaP')

    ws.onmessage = function (m) {
      const [status, sdata] = m.data.split(/:(.+)?/, 2)
      const data = JSON.parse(sdata)
      switch (status) {
        case '1':
          self.onstart()
          break
        case '2':
          self.onparamvalue(data)
          break
        case '3':
          self.onparamvalue(data)
          ws.close()
          break
        case '4':
          self.ontimeout()
          ws.close()
          break
      }
    }

    ws.onclose = function () {
      self.onclose()
    }
  }

  this.requestList = function () {
    const url = Url.format({
      protocol: Config.ws,
      hostname: Config.hostname,
      port: Config.port,
      pathname: `/mavlink/${esid}/parameters`
    })
    sendto(url)
  }

  this.requestRead = function (index) {
    const url = Url.format({
      protocol: Config.ws,
      hostname: Config.hostname,
      port: Config.port,
      pathname: `/mavlink/${esid}/parameters/${index}`
    })
    sendto(url)
  }

  this.paramSet = function (id, value, type, component) {
    const url = Url.format({
      protocol: Config.ws,
      hostname: Config.hostname,
      port: Config.port,
      pathname: `/mavlink/${esid}/parameter/${id}`,
      query: {value, type, component}
    })
    sendto(url)
  }

  this.onstart = function () {}
  this.onparamvalue = function (param) {}
  this.ontimeout = function () {}
  this.onclose = function () {}
}

const API = function () {
  this.paramRequestList = function (esid) {
    const parap = new ParaP(esid)
    parap.requestList()
    return parap
  }
  this.paramRequestRead = function (esid, index) {
    const parap = new ParaP(esid)
    parap.requestRead(index)
    return parap
  }
  this.paramSet = function (esid, id, value, type, component) {
    const parap = new ParaP(esid)
    parap.paramSet(id, value, type, component)
    return parap
  }
}

export default API
