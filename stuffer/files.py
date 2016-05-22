from pathlib import Path

from stuffer import content
from stuffer.core import Action


class Content(Action):
    """Set the contents of a file."""

    def __init__(self, path, contents):
        self.path = Path(path)
        self.contents = content.supplier(contents)
        super(Content, self).__init__()

    def run(self):
        write_file_atomically(self.path, self.contents())


def write_file_atomically(path, contents, suffix=".stuffer_tmp"):
    tmp_file = path.with_suffix(path.suffix + suffix)
    with tmp_file.open('w') as tmp:
        tmp.write(contents)
    try:
        tmp_file.replace(path)
    except:
        if path.exists() and tmp_file.exists():
            tmp_file.unlink()
        raise
