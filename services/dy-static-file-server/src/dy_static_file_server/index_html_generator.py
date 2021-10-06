import os
from typing import List
from textwrap import dedent
from datetime import datetime
from pathlib import Path
from functools import lru_cache

DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"

REFRESH_INTERVAL: int = 5


def _get_dir_files(dir_path: Path) -> List[str]:
    return [
        str(x).replace(str(dir_path), "") for x in dir_path.rglob("*") if x.is_file()
    ]


@lru_cache()
def _get_server_root() -> Path:
    if os.environ.get("SIMCORE_NODE_BASEPATH", None) is None:
        return Path(os.environ["SERVER_ROOT"])

    # when in legacy boot mode
    node_base_path = os.environ["SIMCORE_NODE_BASEPATH"].strip("/")
    return Path(os.environ["SERVER_ROOT"]) / node_base_path


def get_index_path() -> Path:
    return Path(f"{_get_server_root()}/index.html")


def get_last_change_timestamp(str_path: str) -> str:
    file_path = _get_server_root() / str_path.strip("/")
    return datetime.fromtimestamp(file_path.stat().st_mtime).strftime(DATETIME_FORMAT)


def _get_index_content() -> str:
    """
    Generates index.html content.
    - lists all the files inside SERVER_ROOT
    - reloads every second to be updated
    """

    files = _get_dir_files(_get_server_root())

    rendered_file_list = "\n".join(
        [
            f'<li>{get_last_change_timestamp(x)} <a href="{x}">{x}</a></li>'
            for x in files
        ]
    )

    utc_time_stamp = datetime.utcnow().strftime(DATETIME_FORMAT)

    rendered_page = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="{REFRESH_INTERVAL}">
        </head>
        <body>
            <h1>Listing files</h1> <br>
            
            <ul>
                {rendered_file_list}
            </ul>
            
            <br>
            <br>* Last recreated {utc_time_stamp}
            <br>* Content is recrated if there is a change in the inputs directory.
            <br>* Page is refreshed every {REFRESH_INTERVAL} seconds.
        </body>
    </html>
    """
    return dedent(rendered_page)


def generate_index() -> None:
    index_html_path = get_index_path()
    index_html_path.touch()

    index_html_path.write_text(_get_index_content())
    print(f"Regenerated {index_html_path}")