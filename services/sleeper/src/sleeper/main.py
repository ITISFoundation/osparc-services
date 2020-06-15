import os
import json
import random
import time
import subprocess

from pathlib import Path
from typing import Any, Optional, Callable


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


def test_gpu_cuda_code() -> None:
    """Dose some computation on the GPU with CUDA"""
    if get_from_environ("DISABLE_GPU_FOR_TESTING") is not None:
        print("GPU payload disabled for testing")
        return

    # if the command exists it can run on the hardware below
    proc = subprocess.Popen(["nvidia-smi"], stdout=subprocess.PIPE)
    stdout, _ = proc.communicate()
    str_stdout = stdout.decode()
    assert "NVIDIA-SMI" in str_stdout, str_stdout
    assert proc.returncode == 0
    # search the history for the CUDA implementation


def sleep_with_payload(
    amount_to_sleep: int, target_payload: Optional[Callable] = None
) -> None:
    """On each interaction will run the target_payload and then sleep
    Used for validating different types of payloads based on their
    resource requirements.
    """
    print("Will sleep for %s seconds", amount_to_sleep)
    for seconds in range(amount_to_sleep):
        print("[PROGRESS] %s/%s...", seconds + 1, amount_to_sleep)

        start = time.time()
        if target_payload:
            target_payload()
        # take into account the runtime of the target_payload
        time_to_sleep = max(0.0, 1.0 - (time.time() - start))
        print("Remaining sleep time %s", time_to_sleep)

        time.sleep(time_to_sleep)


def main() -> None:
    """
    Will sleep a random amount between INPUT_1 and INPUT_2 values. If 
    these are not provided or are negative random values between 
    1 and 9 will be used.

    INPUT_3 will cause this script to fail after sleeping.
    """

    file_with_int_number = Path(get_from_environ("INPUT_1"))
    sleep_interval = int(get_from_environ("INPUT_2", get_random_sleep()))
    fail_after_sleep = cast_bool(get_from_environ("INPUT_3", "false"))
    output_folder = Path(get_from_environ("OUTPUT_FOLDER"))
    # if this was scheduled on a node with GPU support this env variable will exist
    with_gpu_payload = get_from_environ("DOCKER_RESOURCE_VRAM") is not None

    sleep_from_file = get_random_sleep()
    if file_with_int_number.is_file():
        sleep_from_file = int(file_with_int_number.read_text().strip())
    else:
        print("Could not find file %s", file_with_int_number)

    amount_to_sleep = (
        ensure_sleep_policy(sleep_interval) + ensure_sleep_policy(sleep_from_file)
    ) // 2

    sleep_payload_function = None

    # check if there is GPU support for this container
    if with_gpu_payload:
        sleep_payload_function = test_gpu_cuda_code

    sleep_with_payload(
        amount_to_sleep=amount_to_sleep, target_payload=sleep_payload_function
    )

    # writing program outputs
    output_3_file = output_folder / "single_number.txt"
    output_3_file.write_text(str(get_random_sleep()))

    output_json_content = {"output_2": get_random_sleep()}
    output_json = output_folder / "outputs.json"
    output_json.write_text(json.dumps(output_json_content))

    # Last step should be to fail
    if fail_after_sleep:
        raise Exception("Failing after sleep as requested")


if __name__ == "__main__":
    main()
