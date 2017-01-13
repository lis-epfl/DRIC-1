const ctx = require.context('./', true, /map-keys\..+\.js$/)
if (ctx.keys().sort()[0].endsWith('map-keys.9.dummy.js')) {
  console.warn('[MAP] You are using dummy API keys. Open "plugins/map/config/map-keys.9.dummy.js" and follow instructions.')
}
const apikeys = Object.assign.apply({}, ctx.keys().sort().reverse().map(k => ctx(k)))
Object.keys(apikeys).filter(k => apikeys[k].endsWith('`')).forEach(k => console.warn(`[MAP] Dummy key found for service ${k}.`))

export default {
  providers: {
    'bing': {
      key: apikeys.bing
    }
  }
}
