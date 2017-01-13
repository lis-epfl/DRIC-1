/* eslint-disable */
import Url from 'url'
import Config from '../../../config'
import WebSocketClient from 'websocket.js'
import $ from 'jquery'
import MavlinkAPI from '../../mavlink/api'
import {getTilenames} from './getTilenames'

const API = function () {
  const self = this
  const mavlinkAPI = new MavlinkAPI()
  const url = Url.format({
    protocol: Config.ws,
    hostname: Config.hostname,
    port: Config.port,
    pathname: '/map/waypoint'
  })

  const socket = new WebSocketClient(url)

  socket.onmessage = function (msg) {
    const message = JSON.parse(msg.data)
    switch (message.command) {
      case 'MISSION_COUNT':
      self.updateMissionCount(message.data.count, message.esid, message)
      break
      case 'MISSION_ITEM':
      self.updateMissionItem(message.data, message.esid, message)
      break
      case 'MISSION_CURRENT':
      self.updateMissionCurrent(message.data.seq, message.esid, message)
      break
      case 'MISSION_ACK':
      self.updateMissionAck(message.data.type, message.esid, message)
      break
      case 'MISSION_ITEM_REACHED':
      self.updateMissionReached(message.data.seq, message.esid, message)
      break
    }
  }

  this.readFromVehicle = function (esid) {
    const command = {
      command: 'WS_READ_LIST',
      data: { esid },
      esid
    }
    socket.send(JSON.stringify(command))
  }
  this.writeToVehicle = function (esid, waypoints) {
    const command = {
      command: 'WS_WRITE_LIST',
      data: { waypoints },
      esid
    }
    socket.send(JSON.stringify(command))
  }
  this.setCurrent = function (esid, seq) {
    const command = {
      command: 'WS_SET_CURRENT',
      data:{
        seq: seq
      },
      esid
    }
    socket.send(JSON.stringify(command))
  }

  this.getAvailableCommands = function (esids, callback) {
    return mavlinkAPI.getAvailableCommands(esids, callback)
  }

  this.getAvailableFrames = function (esids, callback) {
    return mavlinkAPI.getEnum('MAV_FRAME', esids, callback)
  }

  this.updateMissionCount = function () {}
  this.updateMissionAck = function () {}
  this.updateMissionCurrent = function () {}
  this.updateMissionReached = function () {}
  this.updateMissionItem = function () {}

  this.getTilenames = getTilenames
  this.getInfos = function (overlayName, cb) {
    $.getJSON(Url.format({
      protocol: Config.http,
      hostname: Config.hostname,
      port: Config.port,
      pathname: `/map/${overlayName}`
    }), function (d) {
      d.url = Url.format({
        protocol: Config.http,
        hostname: Config.hostname,
        port: Config.port,
        pathname: `/map/full/${overlayName}/${d.file}`
      })
      cb(d)
    })
  }
}
export default API
