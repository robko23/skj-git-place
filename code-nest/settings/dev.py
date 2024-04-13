# noinspection PyUnresolvedReferences
from ._base import *

SSH_FOLDER = DATA_DIR / ".ssh"
SSH_AUTHORIZED_KEYS_FILE = SSH_FOLDER / "authorized_keys"
GIT_HOOKS_DIR = BASE_DIR / "docker" / "git-hooks"
