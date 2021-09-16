import logging
import random
from pathlib import Path
from typing import List
import uuid

TARGET_DIRECTORY = Path("/workdir/generated-data")

logger = logging.getLogger(__name__)


def make_random_file(target_dir: Path) -> None:
    file_path = target_dir / f"{uuid.uuid4()}.txt"
    file_path.write_text("no random data here")


def get_files_in_directory(directory: Path) -> List[Path]:
    # pylint: disable=unnecessary-comprehension
    return [x for x in directory.rglob("*")]


def is_content_present(directory: Path) -> bool:
    return len(get_files_in_directory(directory)) > 0


def ensure_random_data(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)

    if is_content_present(target_dir):
        logger.info(
            "Skipping content genration. Already detected %s",
            get_files_in_directory(target_dir),
        )
        return

    for _ in range(random.randint(1, 10)):
        make_random_file(target_dir)


def main() -> None:
    TARGET_DIRECTORY.mkdir(parents=True, exist_ok=True)
    ensure_random_data(TARGET_DIRECTORY)


if __name__ == "__main__":
    main()