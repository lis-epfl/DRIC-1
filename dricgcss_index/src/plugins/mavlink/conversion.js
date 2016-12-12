var stringHash = require('string-hash')
var Parser = require('expr-eval').Parser

const parser = new Parser()

if (typeof window.Conversion === 'undefined') {
  var Conversion = {}
  window.Conversion = Conversion
}

Conversion = window.Conversion

var cache = {}
function recursiveSearch (from, to, shisto) {
  var path = null
  if (from === to) {
    return []
  }
  for (key in shisto) {
    if (shisto[key].from === from) {
      return null
    }
  }
  for (var i = 0; i < Conversion.edges.length; i++) {
    var edge = Conversion.edges[i]
    var key = stringHash(edge.from + edge.to)
    if (!(key in shisto) && edge.from === from) {
      shisto[key] = edge
      var newPath = recursiveSearch(edge.to, to, shisto)
      shisto[key] = null
      delete shisto[key]
      if (newPath !== null && (path === null || newPath.length > path.length)) {
        path = newPath.slice()
        path.push(Conversion.edges[i])
      }
    }
  }
  return path
}

function findShortestConversionPath (from, to) {
  var path = recursiveSearch(from, to, {})
  return path
}

export const convert = function (from, to, value) {
  var key = stringHash(from + to)
  var compiled = null
  if (!(key in cache)) {
    var path = findShortestConversionPath(from, to)
    if (path === null) {
      compiled = null
    } else {
      compiled = parser.parse('x')
      for (var i = 0; i < path.length; i++) {
        compiled = compiled.substitute('x', path[i].expr)
      }
    }
    cache[key] = compiled
  }

  compiled = cache[key]
  if (compiled === null) {
    return null
  }
  return compiled.evaluate({x: value})
}
