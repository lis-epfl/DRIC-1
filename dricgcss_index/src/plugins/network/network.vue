<template>
  <div>
    <p>IP address: <code>{{ip}}</code></p>
    <button role="button" id="network-refresh" class="btn btn-primary"><i class="fa fa-refresh" aria-hidden="true"></i></button>
    <span id="network-refresh-message"></span>
    <table class="table network">
      <thead>
        <tr><th>Client IP</th><th>Client name</th></tr>
      </thead>
      <tbody>
      </tbody>
    </table>
  </div>
</template>
<script>
export default {
  data () {
    return {
      ip: '?.?.?.?'
    }
  }
}
</script>
<style>
</style>
