You are working in a Frappe Framework v16 bench at `/workspace/frappe-bench`.
The site is `acme.localhost` and the custom app is `acme` (module "Acme").
MariaDB and Redis are already running. Do not modify the `frappe` app.

## Task

People at Acme assign work with Frappe's built-in **ToDo** DocType. A ToDo can
point at another document through its `reference_type` and `reference_name`
fields.

When a ToDo that points at another document is closed, add a comment on that
document so its timeline shows the work is done:

- The comment is an `Info` comment whose content is `Task closed: ` followed by
  the ToDo's description.
- Add the comment when the ToDo's status changes to `Closed`. Saving an
  already closed ToDo again must not add another comment. Reopening and
  closing it again adds a new comment.
- ToDos without a reference document must keep working with no comment and no
  error.
- Cancelling a ToDo adds no comment.

Implement this in the `acme` app.
