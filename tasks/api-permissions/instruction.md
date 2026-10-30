You are working in a Frappe Framework v16 bench at `/workspace/frappe-bench`.
The site is `acme.localhost` and the custom app is `acme` (module "Acme").
MariaDB and Redis are already running. Do not modify the `frappe` app.

## Task

The `acme` app has an **Equipment Request** DocType. Employees request
equipment, and approvers approve or reject requests. Fields: `requested_by`
(Link to User), `item`, `cost`, `status` (Pending, Approved or Rejected) and
`decided_by` (Link to User).

Add two API methods in a new module `acme/equipment.py`. Clients will call them
at `/api/method/acme.equipment.<name>`.

### `get_my_requests()`

Returns the logged-in user's own requests, newest first. Each entry has
`name`, `item`, `cost` and `status`. Guests must not be able to call it.

### `decide(name, decision)`

Approves or rejects one request.

- `decision` is `"Approved"` or `"Rejected"`. Any other value is a validation
  error.
- Only users with the **Equipment Approver** role may call it. Anyone else gets
  a permission error.
- Approvers must not decide their own requests. That is a permission error.
- Only `Pending` requests can be decided. Deciding any other request is a
  validation error.
- Set `status` to the decision and `decided_by` to the current user.
- The method changes data, so it must accept only POST requests.
