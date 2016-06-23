from pathlib import Path

from stuffer import content
from stuffer.files import write_file_atomically
from stuffer import store
from .core import Action, run_cmd


UPDATE_NEEDED_KEY = "stuffer.apt.update_needed"

class Install(Action):
    """Install a package with apt-get install."""

    def __init__(self, package):
        self.packages = [package] if isinstance(package, str) else list(package)
        super(Install, self).__init__()

    def run(self):
        if store.get(UPDATE_NEEDED_KEY) != "False":
            run_cmd(["apt-get", "update"])
            store.Set(UPDATE_NEEDED_KEY, "False").run()
        run_cmd(["apt-get", "install", "--yes"] + self.packages)


class AddRepository(Action):
    """Add an apt repository with apt-add-repository"""

    def __init__(self, name):
        self.name = name
        super(AddRepository, self).__init__()

    def prerequisites(self):
        return [Install("software-properties-common")]

    def run(self):
        run_cmd(["add-apt-repository", "--yes", self.name])
        store.Set(UPDATE_NEEDED_KEY, "True").run()


class KeyAdd(Action):
    """Add a trusted key to apt using apt-key add method."""

    def __init__(self, url):
        self.url = url
        super(KeyAdd, self).__init__()

    def prerequisites(self):
        return [Install('wget')]

    def run(self):
        run_cmd("wget {} -O - | apt-key add -".format(self.url), shell=True)
        store.Set(UPDATE_NEEDED_KEY, "True").run()


class KeyRecv(Action):
    """Add a trusted key to apt using apt-key --recv-keys method."""

    def __init__(self, keyserver, key):
        self.keyserver = keyserver
        self.key = key
        super(KeyRecv, self).__init__()

    def run(self):
        run_cmd(["apt-key", "adv", "--keyserver", self.keyserver, "--recv-keys", self.key])
        store.Set(UPDATE_NEEDED_KEY, "True").run()


class SourceList(Action):
    def __init__(self, name, contents):
        self.name = name
        self.contents = content.supplier(contents)
        super(SourceList, self).__init__()

    def prerequisites(self):
        return [Install('apt-transport-https')]

    def run(self):
        write_file_atomically(Path("/etc/apt/sources.list.d").joinpath(self.name).with_suffix(".list"),
                              self.contents().rstrip() + "\n")
        store.Set(UPDATE_NEEDED_KEY, "True").run()
