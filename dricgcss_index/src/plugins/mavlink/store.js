import * as types from './types.js'
import API from './api'
import Config from './config'

const __ = '_mavlink/'
const _TYPE_UNSUBSCRIBE_ALL = __ + '_TYPE_UNSUBSCRIBE_ALL'
const _TYPE_SUBSCRIBE = __ + '_TYPE_SUBSCRIBE'
const _TYPE_MESSAGE_DICT = __ + '_TYPE_MESSAGE_DICT'

const api = new API(Config)
const Subscriber = function (esid, messageType, commit) {
  const websocket = api.createMessageTypeWebsocket(esid, messageType)

  websocket.onmessage = function (m) {
    let view = new DataView(m.data)
    let time = view.getFloat64(0)
    let jsonText = view.getString(8)
    let message = JSON.parse(jsonText)

    commit(_TYPE_MESSAGE_DICT, {message, time, esid, messageType})
  }

  this.unsubscribe = function () {
    console.log(esid, messageType)
    if (websocket !== null) {
      websocket.close()
    }
  }
}

export default {
  state: {
    shownMessageType: null,
    subscribers: [],
    message: {}
  },
  mutations: {
    [types.MESSAGE_TYPE] (state, messageType) {
      state.shownMessageType = messageType
    },
    [_TYPE_UNSUBSCRIBE_ALL] (state) {
      /** Unsubscibe all subscribers */
      state.subscribers.splice(0, state.subscribers.length).forEach(s => s.unsubscribe())
    },
    [_TYPE_SUBSCRIBE] (state, subscriber) {
      /** Add subscriber */
      state.subscribers.push(subscriber)
    },
    [_TYPE_MESSAGE_DICT] (state, messageDict) {
      /** set message to messageDict */
      state.message = messageDict
    }
  },
  getters: {
    [types.GET_INSPECTED_MESSAGE_TYPE] (state) {
      return state.shownMessageType
    },
    [types.SHOWN_MESSAGE_CONTENT] (state) {
      return state.message.message
    },
    [types.SHOWN_MESSAGE_TIME] (state) {
      return state.message.time
    },
    [types.SHOWN_MESSAGE_TYPE] (state) {
      return state.message.messageType
    },
    [types.SHOWN_MESSAGE_ESID] (state) {
      return state.message.esid
    }
  },
  actions: {
    async [types.SHOW_MESSAGE_TYPE] (context, messageType) {
      context.commit(types.MESSAGE_TYPE, messageType)

      // Unsubscibe and clear message
      context.commit(_TYPE_UNSUBSCRIBE_ALL)
      context.commit(_TYPE_MESSAGE_DICT, {})

      // Subscribe
      const esidList = context.getters['driconx/ACTIVE_ESIDS']
      esidList.forEach(e => context.commit(_TYPE_SUBSCRIBE, new Subscriber(e, messageType, context.commit)))
    }
  }
}
