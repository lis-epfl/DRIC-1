<template>
  <select>
    <slot></slot>
  </select>
</template>
<script>
export default {
  props: ['options', 'value'],
  mounted: function () {
    var vm = this
    window.$(this.$el)
    .val(this.value)
    // init select2
    .select2({ data: this.options })
    // emit event on change.
    .on('change', function () {
      vm.$emit('input', [this.value])
    })
  },
  watch: {
    value: function (value, oldValue) {
      if (value[0] === oldValue[0]) {
        return
      }
      // update value
      window.$(this.$el).select2('val', [value])
    },
    options: function (options) {
      // update options
      window.$(this.$el).select2({ data: options, theme: 'bootstrap' })
    }
  },
  destroyed: function () {
    window.$(this.$el).off().select2('destroy')
  }
}
</script>
