You are working in a Frappe Framework v16 bench at `/workspace/frappe-bench`.
The site is `acme.localhost` and the custom app is `acme` (module "Acme").
MariaDB and Redis are already running. Do not modify the `frappe` app.

## Task

Acme wants to book meeting rooms. Create a DocType named **Room Booking** in
the `acme` app, module "Acme", with these fields:

| Field       | Type     | Required |
| ----------- | -------- | -------- |
| `room`      | Data     | yes      |
| `starts_at` | Datetime | yes      |
| `ends_at`   | Datetime | yes      |
| `attendees` | Int      | no       |

Enforce these rules whenever a booking is saved:

1. `ends_at` must be later than `starts_at`.
2. Two bookings for the same room must not overlap. Bookings that only touch,
   where one ends at the exact time the next one starts, are allowed.

Report a broken rule as a validation error, the standard Frappe way.

When you are done, the DocType must exist in the site's database.
