# Palgate Actions (Services)

This integration exposes several actions for querying and managing the list of users authorized for a gate. These can be used in automations, scripts, or via the Developer Tools UI.

All actions identify the gate via `entity_id` passed under `data`:

```yaml
action: palgate.get_device_users
data:
  entity_id: cover.my_gate
```

---

## Actions

### `palgate.get_device_users`
Retrieve the full list of authorized users for a gate.

| Field | Required | Description |
|-------|----------|-------------|
| `entity_id` | Yes | Cover entity of the gate |

Returns: `count` (int) and `users` (list of user records), identified by their unique id - typically, a phone number.

---

### `palgate.get_user_settings`
Retrieve the full user record for a single user.

| Field | Required | Description |
|-------|----------|-------------|
| `entity_id` | Yes | Cover entity of the gate |
| `phone` | Yes | International format phone number (e.g. `972501234567`) |

Returns: the user's record as returned by the Palgate API.

---

### `palgate.add_user`
Add a new authorized user to a gate.

| Field | Required | Description |
|-------|----------|-------------|
| `entity_id` | Yes | Cover entity of the gate |
| `phone` | Yes | International format phone number of the user to add |
| `settings` | No | Dict of additional user fields (see below) |

The `settings` dict is passed directly to the Palgate API. Useful fields include:

```yaml
settings:
  admin: false          # user granted admin privileges for gate
  firstname: "John"
  lastname: "Doe"
  output1: true         # user allowed triggering relay 1
  output2: false        # user allowed triggering relay 2
  output1Latch: false   # user allowed latching the gate, opened or closed
  dialToOpen: false     # auto-open when user dials into controller
  secondaryDevice: true # user allowed to use Linked Devices 
```

Returns: the API response, including user's `id` and whether an SMS invitation was sent.

---

### `palgate.remove_user`
Remove an authorized user from a gate.

| Field | Required | Description |
|-------|----------|-------------|
| `entity_id` | Yes | Cover entity of the gate |
| `phone` | Yes | International format phone number of the user to remove |

---

### `palgate.set_user_settings`
Update an existing user's settings. Only fields provided in `settings` are changed.

| Field | Required | Description |
|-------|----------|-------------|
| `entity_id` | Yes | Cover entity of the gate |
| `phone` | Yes | International format phone number of the user to update |
| `settings` | No | Dict of fields to update (same fields as `add_user`) |

---

### `palgate.get_device_log`
Retrieve the access history log for a gate. Returns a list of access events including who opened the gate, when, and how.

| Field | Required | Description |
|-------|----------|-------------|
| `entity_id` | Yes | Cover entity of the gate |

A few useful fields in the log entries:

```yaml
  userId: "972501234567"      # gate user associated with the log entry
  time: 1234567890            # unix timestamp of event
  reason: 0                   # coded reason of log, 0=success, 1=not authorized, many more
  type: 100                   # type of event, 1=dial, 4=sms, 100=application, 102=Google Home, 110=Siri, many more
  sn: "035555555"             # dial-in phone number
```

---

## Usage in Automations and Scripts

### Add a user when a calendar event starts
```yaml
automation:
  trigger:
    - trigger: calendar
      event: start
      entity_id: calendar.airbnb_bookings
  action:
    - action: palgate.add_user
      data:
        entity_id: cover.front_gate
        phone: "972501234567"
        settings:
          firstname: "Guest"
          output1: true
```

### Remove a user when a calendar event ends
```yaml
automation:
  trigger:
    - trigger: calendar
      event: end
      entity_id: calendar.airbnb_bookings
  action:
    - action: palgate.remove_user
      data:
        entity_id: cover.front_gate
        phone: "972501234567"
```

### Notify when user count changes
> This example requires a pre-created `input_number` helper named `last_known_user_count` (create it via Settings → Devices & Services → Helpers).

```yaml
automation:
  triggers:
    - trigger: time_pattern
      hours: /1   # check every hour
  action:
    - action: palgate.get_device_users
      data:
        entity_id: cover.front_gate
      response_variable: result
    - condition: template
      value_template: |
        {{ result.count != states('input_number.last_known_user_count') | int }}
    - action: notify.mobile_app
      data:
        message: "Gate user count changed: {{ result.count }} users"
    - action: input_number.set_value
      target:
        entity_id: input_number.last_known_user_count
      data:
        value: "{{ result.count }}"
```

---

## Working with Response Data

Actions that return data can be captured via `response_variable` in scripts and automations.

### List all admin users
```yaml
script:
  list_admin_users:
    sequence:
      - action: palgate.get_device_users
        data:
          entity_id: cover.front_gate
        response_variable: result
      - action: notify.mobile_app
        data:
          message: >
            Admins: {{ result.users
              | selectattr('admin', 'eq', true)
              | map(attribute='id')
              | list
              | join(', ') }}
```

### Check if a specific user has access before doing something
```yaml
script:
  check_user_access:
    sequence:
      - action: palgate.get_user_settings
        data:
          entity_id: cover.front_gate
          phone: "972501234567"
        response_variable: user
      - condition: template
        value_template: "{{ user.output1 == true }}"
      - action: notify.mobile_app
        data:
          message: "User {{ user.id }} has relay 1 access"
```

---

## Notes

- Phone numbers must be in **international format** — international prefix, no leading zero or plus sign (e.g. `972501234567` not `0501234567`).
- The `settings` dict is passed through directly to the Palgate API with no field validation on the HA side. Invalid field names or values are silently ignored by the API.
- `entity_id` must be specified under `data:`, not `target:`.
- `get_device_users` fetches all pages transparently — for gates with many users this may take a few seconds.
- These actions require the user calling them to have access to the gate's cover entity.