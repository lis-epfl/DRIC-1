# Events
This component defines two important events.

## `MAVLINK`

When a Mavlink message is received, a `MAVLINK` event is published on the event bus:

| Parameter | Description                        |
|-----------|------------------------------------|
| name      | The message name; e.g. `HEARTBEAT`. |
| esid      | The extended system id. See below. |
| message   | The message content as a dictionnary fieldname => value |


## `SEND_MAVLINK`

Publich a `SEND_MAVLINK` event on the event bus to send a mavlink message:

| Parameter | Description                        |
|-----------|------------------------------------|
| esid      | The extended system id. See below. |
| command   | The message name; e.g. `HEARTBEAT`. |
| parameters| The message content as a dictionnary fieldname => value |

*TODO:* Use same order and names as `MAVLINK` event.

## Extended System Id

The system id is prefixed with the hash of the connection string: `123456789abc-5`

