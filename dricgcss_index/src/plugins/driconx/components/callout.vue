<template>
  <div :class="type">
    <h4>
      <i :class="icon"></i>
      {{title}}
    </h4>
    <p>
      {{text}}
    </p>
  </div>
</template>

<script>
export default {
  name: 'driconx-callout',
  props: ['type', 'icon', 'title', 'text']
}
</script>

<style>

</style>
