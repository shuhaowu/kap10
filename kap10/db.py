from copy import deepcopy
from datetime import datetime
from hashlib import sha1
import json
import os
import subprocess

LOCK_FILE = ".kap10.db.lock"


class LockError(RuntimeError):
  pass


class Database(object):
  def __init__(self, filename):
    self.filename = filename
    self.update()
    self.console = None

  def update(self):
    with open(self.filename) as f:
      self.db = json.load(f)

  def check_password(self, password):
    s = sha1(password).hexdigest()
    for password in self.db["passwords"]:
      if s == password:
        return True

    return False

  def projects(self):
    for k, p in self.db["projects"].iteritems():
      yield k, p

  def get_project(self, project_name, copy=True):
    p = self.db["projects"].get(project_name, None)
    if copy:
      p = deepcopy(p)

    return p

  def is_locked(self):
    return os.path.exists(os.path.join(os.path.dirname(self.filename), LOCK_FILE))

  def lock(self):
    if not self.is_locked():
      f = open(os.path.join(os.path.dirname(self.filename), LOCK_FILE), "w")
      f.close()

  def unlock(self):
    if self.is_locked():
      os.remove(os.path.join(os.path.dirname(self.filename), LOCK_FILE))
      self.console = None

  def update_project(self, project_name, person):
    with open(self.filename, "w") as f:
      project = self.get_project(project_name, copy=False)
      project["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      project["last_updated_by"] = person
      json.dump(self.db, f, indent=4, separators=(',', ': '))

  def get_commit(self, project_name):
    p = self.get_project(project_name)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=p["app_folder"]).strip()

  def run_script(self, project_name, commit):
    self.lock()
    p = self.get_project(project_name)
    # stream this..
    cmd = deepcopy(p["script"])
    cmd.append(commit)
    self.console = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(p["script"][0]))

  def stream_console(self):
    if not self.console:
      raise RuntimeError("No console present!")

    while True:
      data = self.console.stdout.readline()
      if len(data) == 0:
        break

      yield "data: {}\n\n".format(data)

    self.console.poll()
    msg = "script exitted with returncode {}".format(self.console.returncode)

    yield "data: {}\n\n".format("="*(len(msg)))
    yield "data: {}\n\n".format(msg)
    yield "data: {}\n\n".format("="*(len(msg)))
    self.unlock()
