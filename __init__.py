"""Task Tracker: a small py4web app. A list of tasks, and a /cron action a scheduler can call."""
import datetime
import os

from py4web import action, request, redirect, URL, DAL, Field
from pydal.validators import IS_NOT_EMPTY

FOLDER = os.path.join(os.path.dirname(__file__), "databases")
os.makedirs(FOLDER, exist_ok=True)
db = DAL("sqlite://storage.db", folder=FOLDER)
db.define_table(
    "task",
    Field("title", requires=IS_NOT_EMPTY()),
    Field("due", "date"),
    Field("done", "boolean", default=False),
    Field("overdue", "boolean", default=False),
)
db.define_table("cron_run", Field("ran_at", "datetime"), Field("marked", "integer"))

if db(db.task).isempty():
    today = datetime.date.today()
    for title, days in [("Write the release notes", -2), ("Review the pull request", 0), ("Plan the next sprint", 5)]:
        db.task.insert(title=title, due=today + datetime.timedelta(days=days))
    db.commit()


@action("index")
@action.uses("index.html", db)
def index():
    tasks = db(db.task).select(orderby=db.task.done | db.task.due)
    last = db(db.cron_run).select(orderby=~db.cron_run.id, limitby=(0, 1)).first()
    return dict(tasks=tasks, last=last)


@action("add", method="POST")
@action.uses(db)
def add():
    title = (request.forms.get("title") or "").strip()
    if title:
        due = request.forms.get("due") or None
        db.task.insert(title=title, due=due)
    redirect(URL("index"))


@action("toggle/<task_id:int>", method="POST")
@action.uses(db)
def toggle(task_id):
    task = db.task(task_id)
    if task:
        task.update_record(done=not task.done, overdue=False)
    redirect(URL("index"))


@action("cron")
@action.uses(db)
def cron():
    """Called on a schedule: marks every open task past its due date as overdue."""
    today = datetime.date.today()
    marked = db((db.task.done == False) & (db.task.due < today) & (db.task.overdue == False)).update(overdue=True)  # noqa: E712
    db.cron_run.insert(ran_at=datetime.datetime.now(), marked=marked)
    return dict(ok=True, marked=marked, ran_at=str(datetime.datetime.now().replace(microsecond=0)))
