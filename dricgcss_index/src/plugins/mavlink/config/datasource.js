import dric from './dric'
export default {
  protocol: (dric.http === 'https' ? 'wss:' : 'ws'),
  hostname: dric.hostname,
  port: dric.port,
  pathname: '/datasource',
  search: function (sourceName) { return `?s=${sourceName}` }
}
