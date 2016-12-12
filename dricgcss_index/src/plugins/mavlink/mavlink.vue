<template>
  <section class="content body page">
    <section class="content-header">
      <h1>
        Mavlink
      </h1>
      <section class="content">
          <div class="row">
              <div class="col-md-3">
                  <mavlink-battery></mavlink-battery>
              </div>
          </div>
          <div class="row">
            <div class="col-md-4">
              <mavlink-messages-overview></mavlink-messages-overview>
            </div>
            <div class="col-md-4">
              <mavlink-message-viewer></mavlink-message-viewer>
            </div>
          </div>
      </section>
    </section>
  </section>
</template>

<script>
import Battery from './components/battery.vue'
import MessageOverview from './components/messages-overview.vue'
import MessageViewer from './components/message-viewer.vue'
export default {
  components: {
    'mavlink-battery': Battery,
    'mavlink-messages-overview': MessageOverview,
    'mavlink-message-viewer': MessageViewer
  }
}
</script>
