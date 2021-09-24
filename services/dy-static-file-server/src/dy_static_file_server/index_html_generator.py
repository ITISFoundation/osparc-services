import os
from typing import List
from textwrap import dedent
from datetime import datetime
from pathlib import Path


def _get_dir_files(dir_path: Path) -> List[str]:
    return [
        str(x).replace(str(dir_path), "") for x in dir_path.rglob("*") if x.is_file()
    ]


def _get_server_root() -> Path:
    return Path(os.environ["SERVER_ROOT"])


def get_index_path() -> Path:
    return Path(f"{_get_server_root()}/index.html")


def _get_index_content() -> str:
    """
    Generates index.html content.
    - lists all the files inside SERVER_ROOT
    - reloads every second to be updated
    """

    files = _get_dir_files(_get_server_root())

    rendered_file_list = "\n".join([f'<a href="{x}">{x}</a> <br>' for x in files])

    utc_time_stamp = datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")

    refres_interval: int = 5

    rendered_page = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1">
        </head>
        <body>
            <h1>Listing files</h1> <br>

            {rendered_file_list}
            
            <br>
            <br>* Last recreated {utc_time_stamp}
            <br>* Content will be created if there is a change in the ports or the status directory.
            <br>* Page is refreshed every {refres_interval} seconds.
        </body>
    </html>
    """
    return dedent(rendered_page)


def generate_index() -> None:
    index_html_path = get_index_path()

    index_html_path.write_text(_get_index_content())
    print(f"Regenerated {index_html_path}")