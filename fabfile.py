import os

from fabric.api import cd, abort, env, sudo, prefix
from fabric.contrib import files

PROJECT_NAME = "kap10"
GIT_URL = "https://github.com/shuhaowu/kap10.git"
DOMAIN_BASE = "kap10-{}.thekks.net"
DOMAIN = "kap10.thekks.net"
PORT = 9988


def nginx_context():
  return {
    "domain": DOMAIN,
    "port": PORT,
    "name": PROJECT_NAME
  }


FILES = [
  (
    "/etc/nginx/sites-available/{}".format(PROJECT_NAME),
    "configs/nginx",
    nginx_context,
  ),
  (
    "/etc/monit/conf.d/{}".format(PROJECT_NAME),
    "configs/monit",
    {"name": PROJECT_NAME, "port": PORT},
  ),
  (
    "/home/{name}/{name}".format(name=PROJECT_NAME),
    "configs/app_start",
    {"name": PROJECT_NAME, "port": PORT},
  ),
  (
    "/home/{name}/{name}-deploy.sh".format(name=PROJECT_NAME),
    "configs/{name}-deploy.sh".format(name=PROJECT_NAME),
    {"name": PROJECT_NAME}
  )
]

APP_SETTINGS_FILES = [
  (
    "/home/{name}/app/database.json".format(name=PROJECT_NAME),
    "configs/database.json",
    {},
    True
  ),
  (
    "/home/{name}/app/settings_local.py".format(name=PROJECT_NAME),
    "configs/settings_local.py",
    {},
    False
  )
]


home_dir = "/home/{}".format(PROJECT_NAME)
app_dir = home_dir + "/app"
logs_dir = home_dir + "/logs"
venv_dir = home_dir + "/venv"
venv_backup_dir = home_dir + "/venv-backup"


def setup_user():
  if not files.contains("/etc/passwd", PROJECT_NAME):
    sudo("groupadd {}".format(PROJECT_NAME))
    sudo("useradd -d {home_dir} -m -g {name} -s /usr/bin/nologin {name}".format(home_dir=home_dir, name=PROJECT_NAME))


def ensure_packages_installed():
  sudo("apt-get install -y nginx monit libevent-dev")


def setup_directory_structure():
  sudo("mkdir -p {}".format(app_dir))
  sudo("mkdir -p {}".format(logs_dir))
  sudo("mkdir -p {}".format(venv_dir))
  sudo("touch {}/nginx-access.log".format(logs_dir))
  sudo("touch {}/nginx-error.log".format(logs_dir))
  sudo("chown {name}:{name} {logs_dir}/nginx-access.log".format(name=PROJECT_NAME, logs_dir=logs_dir))
  sudo("chown {name}:{name} {logs_dir}/nginx-error.log".format(name=PROJECT_NAME, logs_dir=logs_dir))


def backup_current_venv():
  sudo("rm -rf {}".format(venv_backup_dir))
  if files.exists(venv_dir):
    sudo("cp -r {} {}".format(venv_dir, venv_backup_dir))


def create_new_venv():
  sudo("rm -rf {}".format(venv_dir))
  with cd(home_dir):
    sudo("mkdir venv")
    sudo("virtualenv venv")


def setup_configuration_files():
  for remotepath, localpath, context in FILES:

    if callable(context):
      context = context()

    files.upload_template(localpath, remotepath, context, use_sudo=True, backup=False)
    sudo("chown root:root {}".format(remotepath))

  if not files.is_link("/etc/nginx/sites-enabled/{name}".format(name=PROJECT_NAME)):
    sudo("ln -s /etc/nginx/sites-available/{name} /etc/nginx/sites-enabled/{name}".format(name=PROJECT_NAME))
  sudo("chmod +x {home_dir}/kap10-deploy.sh".format(home_dir=home_dir))
  sudo("chmod +x {home_dir}/kap10".format(home_dir=home_dir))


def setup_fabric_login_key_for_root():
  sudo("mkdir -p /root/.ssh")
  with cd("/root/.ssh"):
    if not files.exists("/root/.ssh/id_rsa_kap10_local.pub", use_sudo=True):
      sudo("ssh-keygen -f id_rsa_kap10_local -t rsa -N '' -K2048")
      sudo("cat id_rsa_kap10_local.pub >> authorized_keys")
      sudo("cp id_rsa_kap10_local.pub /home/kap10/root_local_key")

  sudo("chown kap10:kap10 /home/kap10/root_local_key")
  sudo("chmod 400 /home/kap10/root_local_key")


def setup():
  setup_user()
  ensure_packages_installed()
  setup_directory_structure()
  backup_current_venv()
  create_new_venv()
  setup_configuration_files()
  setup_fabric_login_key_for_root()


def sync_project(commit):
  with cd(app_dir):
    if not files.exists(".git"):
      sudo("git init")
      sudo("git remote add source {}".format(GIT_URL))

    sudo("git fetch source")
    if sudo("git checkout {}".format(commit)).failed:
      abort("Checking out of commit {} failed.".format(commit))

  sudo("chown {name}:{name} {app_dir}".format(name=PROJECT_NAME, app_dir=app_dir))


def install_python_requirements():
  with cd(venv_dir):
    with prefix("source bin/activate"):
      sudo("pip install -r {}/requirements.txt".format(app_dir))


def push_app_settings():
  for remotepath, localpath, context, critical in APP_SETTINGS_FILES:
    if not os.path.exists(localpath) and not critical:
      continue

    if callable(context):
      context = context()

    files.upload_template(localpath, remotepath, context, use_sudo=True, backup=True)
    sudo("chown root:root {}".format(remotepath))

  # Project specific thing.
  sudo("chown {name}:{name} {app_dir}/database.json".format(name=PROJECT_NAME, app_dir=app_dir))


def deploy(commit="master"):
  backup_current_venv()
  create_new_venv()
  sync_project(commit)
  install_python_requirements()
  push_app_settings()
