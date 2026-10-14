# Task Tracker

A small [py4web](https://py4web.com) app: a list of tasks you can add and tick off, and a `cron` action for a
scheduler to call. Each call marks the open tasks past their due date as overdue.

Put the folder in your py4web `apps/` as `tasktracker`, then open `/tasktracker`. The scheduled job calls
`/tasktracker/cron` (daily is plenty).

Licence: BSD 3-Clause.
