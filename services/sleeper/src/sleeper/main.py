import json
import os
import random
import string
import subprocess
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any


def get_from_environ(key: str, default: Any = None) -> str:
    """Returns a value from the environ if not found None"""
    return os.environ.get(key, default)


def get_random_sleep() -> int:
    """Returns a random amount of sleep between 1 and 9"""
    return random.randint(1, 9)


def cast_bool(value: str) -> bool:
    """Cast a probable true string value to a boolean"""
    return value.lower() in {"true", "yes", "1"}


def ensure_sleep_policy(sleep_interval: int) -> int:
    """If the sleep interval is negative a value
    in range [1:9] is returned, otherwise the original
    value"""
    return sleep_interval if sleep_interval >= 0 else get_random_sleep()


def test_mpi_code() -> None:
    """Does nothing for now, not interested in checking MPI capabilities"""
    print("MPI code checking is disabled")


def get_gpu_info() -> str:
    """Returns nvidia-smi's output"""
    proc = subprocess.Popen(["nvidia-smi"], stdout=subprocess.PIPE)
    stdout, _ = proc.communicate()
    str_stdout = stdout.decode()
    assert "NVIDIA-SMI" in str_stdout, str_stdout
    assert proc.returncode == 0
    return str_stdout


def test_gpu_cuda_code() -> None:
    """Does some computation on the GPU with CUDA"""
    if get_from_environ("DISABLE_GPU_FOR_TESTING") is not None:
        print("GPU payload disabled for testing")
        return

    # if the command exists it can run on the hardware below
    get_gpu_info()
    # search the history for the CUDA implementation


def walk_to_bed(amount_to_walk: int = 0) -> None:
    if amount_to_walk > 0:
        print(f"🥱 So tired, I first need to walk {amount_to_walk} meters to bed")
        total_steps = 2 * amount_to_walk
        for step in range(total_steps):
            remaining_meters = amount_to_walk - (step + 1) * 0.5
            print(
                f"👣 Step {step + 1}/{total_steps} - {remaining_meters:.1f}m remaining"
            )
            time.sleep(0.5)


def get_available_cpus() -> int:
    """Returns the number of CPUs available to this process (cgroup/cpuset aware)"""
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:
        return os.cpu_count() or 1


def get_available_memory_bytes() -> int:
    """Returns the memory limit visible to this container, falling back to the host total"""
    for cgroup_file in (
        Path("/sys/fs/cgroup/memory.max"),  # cgroup v2
        Path("/sys/fs/cgroup/memory/memory.limit_in_bytes"),  # cgroup v1
    ):
        if cgroup_file.is_file():
            value = cgroup_file.read_text().strip()
            if value.isdigit():
                return int(value)
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemTotal:"):
            return int(line.split()[1]) * 1024
    return 0


def print_available_resources(enforce_gpu_support: bool = False) -> None:
    print(f"🖥️  Available CPUs: {get_available_cpus()}", flush=True)
    print(
        f"🧠 Available memory: {get_available_memory_bytes() / (1024**3):.2f} GiB",
        flush=True,
    )
    if enforce_gpu_support and get_from_environ("DISABLE_GPU_FOR_TESTING") is None:
        print(get_gpu_info(), flush=True)


def snore() -> None:
    """Logs a random snoring sound"""
    print(
        "💤 "
        + random.choice(
            ["Zzzz...", "Zzzzzz...", "Xrrrr...", "Hhhrrrr...", "Zzz-honk!"]
        ),
        flush=True,
    )


def generate_random_words(word_length, total_length):
    words = []
    while total_length > 0:
        word = "".join(
            random.choices(
                string.ascii_lowercase + string.ascii_uppercase, k=word_length
            )
        )
        spacer = " " if total_length > word_length else ""
        words.append(word + spacer)
        total_length -= word_length + len(spacer)
    return "".join(words)


def dream(output_folder: Path, dream_size_byte: int) -> None:
    output_3_file = output_folder / "dream.txt"
    with output_3_file.open("wb") as fp:
        psychedelic_content = generate_random_words(6, dream_size_byte).encode()
        fp.write(psychedelic_content)
        fp.truncate(dream_size_byte)
    print(f"What a dream! it was {dream_size_byte}!! Amazing!")


def sleep_with_payload(
    amount_to_sleep: int,
    target_payload: Callable | None = None,
    snore_rate: int = 0,
) -> None:
    """On each interaction will run the target_payload and then sleep
    Used for validating different types of payloads based on their
    resource requirements.

    snore_rate: number of random snoring logs emitted per second of sleep (0 disables snoring)
    """
    print(f"😴 Will sleep for {amount_to_sleep} seconds", flush=True)
    for seconds in range(amount_to_sleep):
        print(f"[PROGRESS] {seconds + 1}/{amount_to_sleep}", flush=True)

        start = time.time()
        if target_payload:
            target_payload()
        for _ in range(snore_rate):
            snore()
        # take into account the runtime of the target_payload
        time_to_sleep = max(0.0, 1.0 - (time.time() - start))
        if time_to_sleep == 0.0:
            print(
                "⚠️  No remaining sleep time left this tick: "
                "the payload and/or snoring took a full second or more!",
                flush=True,
            )
        print(f"💤 Remaining sleep time: {time_to_sleep:.2f}s", flush=True)

        time.sleep(time_to_sleep)


def main() -> None:
    """
    Will sleep a random amount between INPUT_1 and INPUT_2 values. If
    these are not provided or are negative random values between
    1 and 9 will be used.

    INPUT_3 will cause this script to fail after sleeping.

    Before sleeping, it will walk first the distance given in INPUT_4.

    INPUT_6 defines a snore rate: random logs emitted per second of sleep.
    If not provided, no snoring happens.
    """

    file_with_int_number = Path(get_from_environ("INPUT_1"))
    sleep_interval = int(get_from_environ("INPUT_2", get_random_sleep()))
    fail_after_sleep = cast_bool(get_from_environ("INPUT_3", "false"))
    walk_distance = int(get_from_environ("INPUT_4", 0))
    dream_size_byte = int(get_from_environ("INPUT_5", 0))
    snore_rate = int(get_from_environ("INPUT_6", 0))
    output_folder = Path(get_from_environ("OUTPUT_FOLDER"))
    # if the service needs to confirm GPU is working
    enforce_gpu_support = get_from_environ("DOCKER_RESOURCE_VRAM") is not None
    # if the service needs to confirm MPI is working
    enforce_mpi_support = get_from_environ("DOCKER_RESOURCE_MPI") is not None

    sleep_from_file = get_random_sleep()
    if file_with_int_number.is_file():
        sleep_from_file = int(file_with_int_number.read_text().strip())
    else:
        print(f"Could not find file {file_with_int_number}")

    print_available_resources(enforce_gpu_support=enforce_gpu_support)

    amount_to_sleep = (
        ensure_sleep_policy(sleep_interval) + ensure_sleep_policy(sleep_from_file)
    ) // 2

    sleep_payload_function = None

    if enforce_gpu_support:
        sleep_payload_function = test_gpu_cuda_code

    if enforce_mpi_support:
        sleep_payload_function = test_mpi_code

    walk_to_bed(amount_to_walk=walk_distance)

    sleep_with_payload(
        amount_to_sleep=amount_to_sleep,
        target_payload=sleep_payload_function,
        snore_rate=snore_rate,
    )

    # writing program outputs
    output_1_file = output_folder / "single_number.txt"
    output_1_file.write_text(str(get_random_sleep()))

    output_json_content = {"output_2": get_random_sleep()}
    output_json = output_folder / "outputs.json"
    output_json.write_text(json.dumps(output_json_content))

    dream(output_folder, dream_size_byte)

    # Last step should be to fail
    if fail_after_sleep:
        raise RuntimeError("Failing after sleep as requested")


if __name__ == "__main__":
    main()
