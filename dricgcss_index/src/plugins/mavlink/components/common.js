/**
 * Watch for driconx/ACTIVE_ESIDS getter change
 * @param  {Function} callback receives an array of esids
 */
export const watchEsidChange = function (callback) {
  if (typeof this.$store.getters['driconx/ACTIVE_ESIDS'] !== 'undefined') {
    this.$store.watch(() => typeof this.$store.getters['driconx/ACTIVE_ESIDS'] !== 'undefined' && this.$store.getters['driconx/ACTIVE_ESIDS'], callback)
  } else {
    console.error('mavlink needs driconx')
  }
}
