import os
import shlex
import subprocess
import sys
import time

import django

django.setup()

ALLOWED_COMMANDS = [
    "git-upload-pack",
    "git-receive-pack",
    "git-upload-archive"
]

if __name__ == '__main__':
    from django.core.cache import cache
    from django.contrib.auth.models import User

    from core.models import Repository

    from core.models import SSHKey

    # openssh-server injects this variable
    original_command = os.getenv("SSH_ORIGINAL_COMMAND")
    if not original_command:
        print("This script is intended to run from ForceCommand openssh-server option",
              file=sys.stderr)
        exit(1)
        pass

    args = shlex.split(original_command)
    cmd = args[0]

    if cmd not in ALLOWED_COMMANDS:
        print("SSH connection working, but is not intended for shell")
        exit(1)

    repo = args[1]
    [username, reponame] = repo.split("/")

    ssh_info = os.getenv("SSH_CLIENT")
    [remote_ip, remote_port, _server_port] = ssh_info.split(" ")

    # Scuffed solution to race condition <3
    tries = 0
    used_ssh_key: SSHKey | None = None
    while tries < 10:
        used_ssh_key = cache.get(f"{remote_ip}:{remote_port}")
        if used_ssh_key:
            break
        elif tries == 10:
            print("Permission denied (no connection log)", file=sys.stderr)
            exit(1)
        time.sleep(0.2)
        tries = tries + 1
    if not used_ssh_key:
        print("Permission denied (no connection log)", file=sys.stderr)
        exit(1)

    try:
        profile = User.objects.get(pk=used_ssh_key.owner.pk, username__exact=username)
        repo = Repository.objects.get(owner=used_ssh_key.owner, slug__exact=reponame)
    except (User.DoesNotExist, Repository.DoesNotExist):
        print("Permission denied (repo not found or user does not have access)", file=sys.stderr)
        exit(1)

    subprocess.run(args)
