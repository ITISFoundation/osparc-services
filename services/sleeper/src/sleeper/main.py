import os
import json
import random
import time
import subprocess


def get_from_environ(key, default=None):
    """Returns a value from the environ if not found None"""
    return os.environ.get(key, default)


def get_random_sleep():
    """Returns a random amount of sleep between 1 and 9"""
    return random.randint(1, 9)


def cast_bool(value):
    """Transformas a string into a boolean"""
    return value.lower() in {"true", "yes", "1"}


def validate_not_negative_int(number):
    """Returns the number if >= 0 or a random int in range [1:9]"""
    return number if number >= 0 else get_random_sleep()


def test_gpu_cuda_code():
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

    # leving here for future usaage
    # from numba import vectorize, cuda
    # import numpy as np

    # a = np.ones(1_000_000, dtype=np.float64)

    # @vectorize(["float64(float64)"], target="cuda")
    # def gpu_function(x):
    #     """sum 1 to all values in array"""
    #     return x + 1

    # gpu_function(a)


def sleep_with_payload(amount_to_sleep, target_payload=lambda: True):
    """On each interaction will run the target_payload and then sleep
    Used for validating different types of payloads based on their
    resource requirements.
    """
    print(f"Will sleep for {amount_to_sleep} seconds")
    for seconds in range(amount_to_sleep):
        print(f"[PROGRESS] {seconds + 1}/{amount_to_sleep}...")

        start = time.time()
        target_payload()
        # take into account the runtime of the target_payload
        time_to_sleep = max(0.0, 1.0 - (time.time() - start))
        print(f"Remaining sleep time {time_to_sleep}")

        time.sleep(time_to_sleep)


def main():
    """
    Will sleep a random amount between INPUT_1 and INPUT_2 values. If 
    these are not provided or are negative random values between 
    1 and 9 will be used.

    INPUT_3 will cause this script to fail after sleeping.
    """

    file_with_int_number = get_from_environ("INPUT_1")
    sleep_interval = int(get_from_environ("INPUT_2", get_random_sleep()))
    fail_after_sleep = cast_bool(get_from_environ("INPUT_3", "false"))
    output_folder = get_from_environ("OUTPUT_FOLDER")
    # if this was scheduled on a node with GPU support this env variable will exist
    with_gpu_payload = get_from_environ("DOCKER_RESOURCE_VRAM") is not None

    sleep_from_file = get_random_sleep()
    if os.path.isfile(file_with_int_number):
        with open(file_with_int_number, "r") as f:
            sleep_from_file = int(f.read().strip())
    else:
        print(f"Could not find file '{file_with_int_number}'")

    amount_to_sleep = (
        validate_not_negative_int(sleep_interval)
        + validate_not_negative_int(sleep_from_file)
    ) // 2

    # check if there is GPU support for this container

    if with_gpu_payload:
        sleep_with_payload(amount_to_sleep, target_payload=test_gpu_cuda_code)
    else:
        sleep_with_payload(amount_to_sleep)

    # writing program outputs
    with open(os.path.join(output_folder, "single_number.txt"), "w") as out_file:
        out_file.write(str(get_random_sleep()))

    with open(os.path.join(output_folder, "outputs.json"), "w") as out_file:
        payload = {"output_2": get_random_sleep()}
        out_file.write(json.dumps(payload))

    # Last step should be to fail
    if fail_after_sleep:
        raise Exception("Failing after sleep as requested")


if __name__ == "__main__":
    main()
