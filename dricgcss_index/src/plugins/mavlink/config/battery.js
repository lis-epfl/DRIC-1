export default {
  mapping: {
    'SYS_STATUS': {
      voltage: 'voltage_battery',
      current: 'current_battery',
      remaining: 'battery_remaining'
    },
    'BATTERY_STATUS': {
      current: 'current_battery',
      remaining: 'battery_remaining'
    },
    'HIGH_LATENCY': {
      remaining: 'battery_remaining'
    }
  }
}
