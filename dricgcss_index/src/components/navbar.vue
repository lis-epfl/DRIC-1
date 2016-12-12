<script>
let navComponents = {}
function requireAll (x) {
  let context = require.context('../plugins/', true, /.*\.vue$/)
  let regexp = new RegExp('(.*/)index\\.js')

  for (let i = 0; i < x.keys().length; i++) {
    let p = x.keys()[i]
    let plugindir = regexp.exec(p)[1]
    let r = x(p)
    if (typeof r.navbar === 'undefined') continue
    for (let k in r.navbar) {
      let target = r.navbar[k]
      for (let j = 0; j < context.keys().length; j++) {
        let candidate = context.keys()[j]
        if (candidate.indexOf(plugindir) === 0) {
          if (candidate.indexOf(target) === plugindir.length) {
            navComponents[k] = context(candidate)
          }
        }
      }
    }
  }
}
requireAll(require.context('../plugins/', true, /\/index.js$/))

export default {
  components: navComponents,
  render: function (h) {
    let deploy =
      (<a href="#" class="sidebar-toggle" data-toggle="offcanvas" role="button">
        <span class="sr-only">Toggle navigation</span>
      </a>)

    let children = [deploy]

    for (let k in navComponents) {
      let navChild = h(navComponents[k])
      children.push(navChild)
    }

    return h(
      'nav', {
        attrs: {
          class: 'navbar navbar-static-top'
        }
      },
      children
    )
  }
}

</script>
