<template>
  <ul class="list-group">
    <li v-for="node in flatContent" class="list-group-item" v-if="showNode(node)" :style="{color: matchSearch(node.entry.text)?'red':''}">
    <i :style="{'user-select': 'none'}" @click="node.collapsed = !node.collapsed" :class="{'un-collapse-btn fa fa-fw': true, 'fa-plus': node.collapsed, 'fa-minus': !node.collapsed}" v-if="'children' in node.entry && node.entry.children.length > 0"></i>
    <i v-for="n in node.level" :style="{'user-select': 'none'}" class="fa fa-fw">&nbsp;</i><span>{{node.entry.text}}</span>
    <div class="form-inline pull-right">
      <div v-for="alt in node.entry.alternatives" class="checkbox" :style="{background: alt.selected ? altcolor(node, alt):'', color: altcolor(node, alt)&&alt.selected ?'white':''}">
        <label>
          <input type="checkbox" class="sourceCheckbox" v-model="alt.selected" @change="select($event, node, alt)" />
          <span>{{alt.text}}</span>
        </label>
        &nbsp;
      </div>
    </div>
  </li>
</ul>
</template>
<script>
import ColorHelper from './ColorHelper'

const colorHelper = new ColorHelper()

function flatten (array, level = 0, parent = null) {
  const out = []
  for (let entry of array) {
    const me = {
      entry,
      level,
      collapsed: true,
      parent,
      selectable: false,
      selected: false,
      altcolors: []
    }
    out.push(me)
    if ('children' in entry && entry.children.length > 0) {
      out.push.apply(out, flatten(entry.children, level + 1, me))
    } else {
      me.selectable = true
    }
  }
  return out
}

export default {
  name: 'tree-view',
  props: ['value', 'search'],
  data () {
    return {
      flatContent: []
    }
  },
  watch: {
    value () {
      this.flatContent = flatten(this.value)
    },
    search () {
      for (let node of this.flatContent) {
        if (this.search.length === 0) {
          node.collapsed = true
        }
        if (this.matchSearch(node.entry.text)) {
          if (node.parent) {
            node.parent.collapsed = false
          }
          if (!(node.entry.children && node.entry.children.find(c => this.matchSearch(c.text)))) {
            node.collapsed = true
          }
        }
      }
    }
  },
  mounted () {
    this.flatContent = flatten(this.value)
    this.$parent.$on('clear', this.clear)
  },
  methods: {
    clear () {
      this.flatContent.filter(n => n.entry.alternatives).forEach(n => n.entry.alternatives.filter(alt => alt.selected).forEach(alt => {
        alt.selected = false
        this.$emit('uncheckedplot', `${n.parent.entry.text}/${n.entry.text}$${alt.text}`)
      }))
    },
    showNode (node) {
      let visible = true
      if (node.parent) {
        visible = !node.parent.collapsed
      } else {
        visible = true
      }
      if (this.search.length > 0) {
        if (this.matchSearch(node.entry.text)) {
          visible = node.parent ? !node.parent.collapsed : true
        } else if (node.parent && this.matchSearch(node.parent.entry.text)) {
          visible = !node.parent.collapsed
        } else if (node.entry.children && node.entry.children.find(c => this.matchSearch(c.text))) {
          visible = true
        } else {
          visible = false
        }
      }
      return visible
    },
    matchSearch (text) {
      if (this.search.length <= 0) { return false }
      return text.toUpperCase().indexOf(this.search.toUpperCase()) >= 0
    },
    select (e, node, alt) {
      const target = `${node.parent.entry.text}/${node.entry.text}$${alt.text}`
      if (typeof node.altcolors.find(ac => ac.alt.text === alt.text) === 'undefined') {
        node.altcolors.push({alt, color: undefined})
      }
      if (alt.selected) {
        const color = colorHelper.nextColor()
        node.altcolors.filter(ac => ac.alt.text === alt.text).forEach(ac => (ac.color = color))
        this.$emit('checkedplot', target, color)
      } else {
        node.altcolors.filter(ac => ac.alt.text === alt.text).forEach(ac => (ac.color = undefined))
        this.$emit('uncheckedplot', target)
      }
    },
    altcolor (node, alt) {
      if (node.altcolors.length === 0) { return }
      const ac = node.altcolors.find(ac => ac.alt.text === alt.text)
      if (typeof ac === 'undefined' || typeof ac.color === 'undefined') { return '' }
      return ac.color
    }
  }
}
</script>
<style>
.un-collapse-btn {
  cursor: pointer;
}
.selectable {
  cursor: pointer;
}
li.selected span {
  color: white;
}
.form-inline {
  display: block;
}
</style>
