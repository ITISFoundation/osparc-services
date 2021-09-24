from pathlib import Path
import os


def _get_server_root() -> Path:
    return Path(os.environ["SERVER_ROOT"])


def get_index_path() -> Path:
    return Path(f"{_get_server_root()}/index.html")


def _get_index_content() -> str:
    return "<h>Hello</h1>"


def generate_index() -> None:
    get_index_path().write_text(_get_index_content())