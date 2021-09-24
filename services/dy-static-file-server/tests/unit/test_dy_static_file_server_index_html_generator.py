# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
from types import ModuleType
from unittest.mock import patch


import pytest

# UTILS


# FIXTURES


@pytest.fixture
def index_html_content() -> str:
    return "some random content here"


# TESTS


def test_can_import_module(
    dy_static_file_server: ModuleType, index_html_content: str
) -> None:
    from dy_static_file_server import index_html_generator

    assert type(index_html_generator) == ModuleType


def test_generate_index_html(
    dy_static_file_server: ModuleType, env_server_root: None, index_html_content: str
) -> None:
    from dy_static_file_server import index_html_generator

    with patch.object(
        index_html_generator, "_get_index_content", return_value=index_html_content
    ):
        index_html_generator.generate_index()

        index_html = index_html_generator.get_index_path()
        assert index_html.read_text() == index_html_content
