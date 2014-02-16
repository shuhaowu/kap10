from __future__ import absolute_import

import os

from flask import Flask, render_template, request, abort, Response
from .db import Database

from settings import APP_FOLDER

app = Flask(__name__,
            static_folder=os.path.join(APP_FOLDER, "static"),
            template_folder=os.path.join(APP_FOLDER, "templates"))
app.config.from_pyfile(os.path.join(APP_FOLDER, "settings.py"))

db = Database(app.config["DATABASE_FILE"])


@app.route("/")
def main():
  projects = []

  i = 0
  for k, p in db.projects():
    if i % 3 == 0:
      projects.append([])

    projects[-1].append((k, p))
    i += 1

  print projects

  return render_template("main.html", projects=projects, db=db, length=i)


@app.route("/deploy/<project>", methods=["POST", "GET"])
def deploy(project):
  id = project
  project = db.get_project(id)

  if request.method == "POST":
    if not db.check_password(request.json["pass"].strip()):
      return abort(403)

    if db.is_locked():
      return abort(503)

    print request.json
    db.run_script(id, request.json["commit"].strip())
    # Last person started is good enough.
    db.update_project(id, request.json["name"])
    return "okay"
  else:
    return render_template("deploy.html", project=project, id=id)


@app.route("/deploystatus/<project>")
def deploystatus(project):
  if not db.is_locked():
    return abort(503)

  return Response(db.stream_console(), mimetype="text/event-stream")
