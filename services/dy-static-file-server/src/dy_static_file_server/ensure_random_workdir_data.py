import random
from pathlib import Path
from typing import List
import uuid
import grp, pwd
import getpass
import os

TARGET_DIRECTORY = Path("/workdir/generated-data")


def make_random_file(target_dir: Path) -> None:
    file_path = target_dir / f"{uuid.uuid4()}.txt"
    file_path.write_text("no random data here")
    print(f"Created {file_path}")


def get_files_in_directory(directory: Path) -> List[Path]:
    # pylint: disable=unnecessary-comprehension
    return [x for x in directory.rglob("*")]


def is_content_present(directory: Path) -> bool:
    return len(get_files_in_directory(directory)) > 0


def print_user_and_directory_info() -> None:
    user = getpass.getuser()
    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
    gid = pwd.getpwnam(user).pw_gid
    groups.append(grp.getgrgid(gid).gr_name)

    print(f"User {user}, groups {groups}")
    os.system("ls -lah /workdir")


def ensure_random_data(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)

    print_user_and_directory_info()

    print(f"Creating {target_dir} if missing")

    if is_content_present(target_dir):
        files = get_files_in_directory(target_dir)
        print(f"Skipping content genration. Already detected: {files}")
        return

    for _ in range(random.randint(1, 10)):
        make_random_file(target_dir)


def main() -> None:
    ensure_random_data(TARGET_DIRECTORY)


if __name__ == "__main__":
    main()